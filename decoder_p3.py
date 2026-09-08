"""P3 copy of the frozen S06E decoder; only candidate transition tags change.

All selection, marginals, relation configuration and candidate-retention logic
is inherited byte-for-byte below the original module docstring.
"""
"""Isolated S06E decoder: parent decisions plus exact marginal export.

The original global_context.py remains frozen. Sequence signatures enter via
the shared S06E adapter; the parent decision policy is retained for comparison.
"""
import json
import math
from r5.legacy_context import finite, group_key
from r5.sequence import decode
from analysis_schema_s06e import signature

def decode_sentence(self,sentence):
    self.s06e_marginals = {}
    tokens=sentence['tokens'];solutions=[];boundaries=[];counts={'lemma_pos_selected_tokens':0,'ambiguous_or_outside_tokens':0,'no_analysis_tokens':0}
    supplied=self.external_scorer(sentence) if self.external_scorer else {}
    if self.external_scorer:
        expected={i:{a['analysis_id'] for a in t['analysis']['analyses']} for i,t in enumerate(tokens)}
        if set(supplied)!=set(expected) or any(set(supplied[i])!=ids for i,ids in expected.items()):raise ValueError('EXTERNAL_SCORE_ID_COVERAGE')
        if any(not math.isfinite(v) for values in supplied.values() for v in values.values()):raise ValueError('NONFINITE_EXTERNAL_SCORE')
    for block in self._sentence_blocks(tokens):
        unaries=self._unaries(tokens,block)
        for i in block:
            for aid,value in supplied.get(i,{}).items():unaries[i][aid]+=value
        configs,bounds,audits=self._configurations(tokens,block,unaries);boundaries.extend(bounds)
        rawdomains=[]
        for i in block:
            candidates=tokens[i]['analysis']['analyses']
            rawdomains.append([{'id':a['analysis_id'],'tag':self.ngram.tag(a),
                                'score':unaries[i][a['analysis_id']]} for a in candidates] or
                              [{'id':'','tag':signature('X' if any(c.isalnum() for c in tokens[i]['raw']) else 'PUNCT',{}),'score':0.}])
        transition=(lambda a,b,c:self.ngram_weight*self.ngram.transition(a,b,c)) if self.ngram else (lambda a,b,c:0.)
        candidates=[];marginals=[{} for _ in block]
        for config in configs:
            domains=[[c for c in domain if i not in config['bindings'] or c['id']==config['bindings'][i]] for i,domain in zip(block,rawdomains)]
            result=decode(domains,transition)
            if result is None:continue
            total=result['score']+config['score']
            candidates.append((total,result['path'],config))
            for local,values in enumerate(result['marginals']):
                for aid,value in values.items():marginals[local][aid]=max(marginals[local].get(aid,-math.inf),value+config['score'])
        candidates.sort(key=lambda x:(-x[0],x[1],json.dumps(x[2]['bindings'],sort_keys=True)))
        best,path,config=candidates[0];chosen=dict(zip(block,path));edges=self._edges(config,chosen,tokens)
        self.s06e_marginals.update({i: dict(marginals[k]) for k, i in enumerate(block)})
        complete=all(tokens[i]['analysis']['search_complete'] for i in block)
        content=[i for i in block if any(c.isalnum() for c in tokens[i]['raw'])]
        for local,i in enumerate(block):
            token=tokens[i];analyses=token['analysis']['analyses'];lookup={a['analysis_id']:a for a in analyses}
            if not analyses:
                decision={'status':'NO_ANALYSIS','selected_analysis':None,'preferred_analysis':None,'selected_pos':None,'retained_analysis_ids':[],'evidence':[]}
                counts['no_analysis_tokens']+=1
            else:
                preferred=lookup[chosen[i]];group=group_key(preferred)
                alt=max((value for aid,value in marginals[local].items() if group_key(lookup[aid])!=group),default=-math.inf)
                margin=best-alt if math.isfinite(alt) else None
                # In a short fragment, frequency alone must not collapse
                # a lexical nominal/event reading into one certain answer.
                lexical=any(a['root_pos']!='VERB' and a['output_pos'] in {'NOUN','ADJ','NUM'} and a['features'].get('Case','Nom')=='Nom' and a['features'].get('VerbForm')!='Fin' for a in analyses)
                event=any(finite(a) or a['features'].get('VerbForm')=='Vnoun' for a in analyses)
                overt_case=any(a['features'].get('Case') in {'Acc','Dat'} for k in content if k!=i for a in tokens[k]['analysis']['analyses'] if a['cost']==min(x['cost'] for x in tokens[k]['analysis']['analyses']))
                fragment=len(content)<=2 and lexical and event and not overt_case
                enough=complete and not fragment and (margin is None or margin>=self.min_margin)
                selected=preferred if enough else None
                within=[aid for aid,v in marginals[local].items() if group_key(lookup[aid])==group and best-v<self.min_margin]
                posalt=max((value for aid,value in marginals[local].items() if lookup[aid]['output_pos']!=preferred['output_pos']),default=-math.inf)
                pos_enough=complete and not fragment and (not math.isfinite(posalt) or best-posalt>=self.min_margin)
                leaders={}
                for aid,value in sorted(marginals[local].items(),key=lambda x:(-x[1],x[0])):leaders.setdefault(group_key(lookup[aid]),value)
                status='GLOBAL_SELECTED' if enough else 'GLOBAL_AMBIGUOUS' if complete else 'INCOMPLETE_CANDIDATE_SEARCH'
                decision={'status':status,'selection_domain':'ALL_EXISTING_CANDIDATE_GROUPS','selected_analysis':selected,
                          'selected_analysis_role':'REPRESENTATIVE_OF_SELECTED_LEMMA_POS_GROUP' if selected else None,
                          'preferred_analysis':preferred,'preference_source':'ONE_SHARED_SENTENCE_ASSIGNMENT',
                          'selected_pos':preferred['output_pos'] if pos_enough else None,'selection_scope':'LEMMA_POS',
                          'group_margin':margin,'margin_scope':'MAX_MARGINAL_WITHIN_RETAINED_CONFIGURATIONS',
                          'calibrated_probability':None,'outer_search_complete':False,
                          'fragment_ambiguity':fragment,
                          'partial_resolution':'POS_ONLY' if pos_enough and not enough else None,
                          'full_path_unique':enough and len(within)==1,'within_group_analysis_ids':within if enough else [],
                          'retained_analysis_ids':[a['analysis_id'] for a in analyses],
                          'ranked_analysis_ids':[aid for aid in sorted(marginals[local],key=lambda aid:(-marginals[local][aid],aid))],
                          'evidence':[{'rule':'GLOBAL_SHARED_PATH','weight':0.,'family':'joint_solution','related_token_indices':block}],
                          'competing_groups':[{'lemma':g[0],'upos':g[1],'score':value} for g,value in leaders.items()]}
                counts['lemma_pos_selected_tokens' if enough else 'ambiguous_or_outside_tokens']+=1
            token['context_decision']=decision;token['selection_status']=decision['status']
        solutions.append({'indices':block,'score':best,'analysis_bindings':{i:aid or None for i,aid in chosen.items()},
                          'relations':edges,'plans':config['plans'],'scope_choice':config['scope_choice'],'scopes':config['scopes'],
                          'candidate_configurations':len(candidates),'configuration_search_exact':False,'sequence_search_exact':True,
                          'plan_inventory':audits,'binding_conflicts':0,'partial_dependency_structure':True})
    sentence['context_selector']=self.manifest();sentence['context_model']='GLOBAL_HYBRID_SEQUENCE_AND_PARTIAL_RELATIONS'
    sentence['global_solutions']=solutions;sentence['clause_boundaries']=boundaries
    sentence['global_parse_status']='CONSISTENT_SHARED_ASSIGNMENT_WITH_PARTIAL_DEPENDENCIES'
    sentence['relation_binding_conflicts']=[];sentence['relation_hypotheses']=[]
    sentence['selection_summary']={**counts,'all_original_candidates_retained':True,'neural_model_used':None if self.external_scorer else False,
                                   'external_scores_used':self.external_scorer is not None,
                                   'statistical_ngram_used':self.ngram_enabled,'binding_conflicts':0,
                                   'relation_edges':sum(len(s['relations']) for s in solutions)}
    return sentence
