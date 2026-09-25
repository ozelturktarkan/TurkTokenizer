//! P128: exact, candidate-bound YONT for a declared small grammar.
//! No candidate/score/ID changes. Consensus is conditional on grammar and inventory.
use std::collections::{BTreeMap,BTreeSet};
use std::io;
use p82::json::{self,V,s,n};
use p82::obj;

#[derive(Clone,Debug)]
struct Person { p:u8, plural:bool }
#[derive(Clone,Debug)]
enum Tag { Nominal{case_:String, person:Person, poss:Option<Person>}, Verb{person:Person} }
#[derive(Clone,Debug)]
struct Candidate { key:String, root:String, tag:Option<Tag>, reason:String, score:V }
#[derive(Clone,Debug)]
struct Token { raw:String,start:usize,end:usize,candidates:Vec<Candidate>,complete:bool }
#[derive(Clone,Debug,PartialEq,Eq,PartialOrd,Ord)]
struct Answer { verb:usize,subject:usize,object:usize,root:String,owner:Option<(usize,usize)> }
struct Search<'a> {
    tokens:&'a [Token],cap:usize,nodes:usize,complete:bool,plans:usize,
    answers:BTreeMap<Answer,V>, selected:Vec<usize>,
}
fn arr(v:&V)->io::Result<&[V]>{if let V::Array(xs)=v{Ok(xs)}else{Err(json::err("array required"))}}
fn person(mid:&str,prefix:&str)->Option<Person>{
    let x=mid.strip_prefix(prefix)?;let (p,num)=x.split_once('_')?;
    let p=p.parse::<u8>().ok()?;if !(1..=3).contains(&p){return None;}
    let plural=match num{"SING"=>false,"PLUR"=>true,_=>return None};Some(Person{p,plural})
}
fn classify(key:&str,frames:&BTreeSet<String>)->io::Result<(String,Option<Tag>,String)>{
    let parsed=json::parse(key)?;let a=arr(&parsed)?;
    if a.len()!=4{return Err(json::err("canonical key shape"));}
    let root=a[0].string()?.to_owned();let rp=a[1].string()?;let fp=a[3].string()?;
    let mut mids=Vec::new();
    for ev in arr(&a[2])? {
        let e=arr(ev)?;if e.len()!=2{return Err(json::err("event pair"));}
        if e[1].string()? != "-" {return Ok((root,None,"UNSUPPORTED_DERIVATION_BOUNDARY".into()));}
        mids.push(e[0].string()?.to_owned());
    }
    let unsupported=|r:&str|Ok((root.clone(),None,r.to_owned()));
    if mids.iter().any(|m|m=="POLARITY_NEG"||m.starts_with("VOICE_")||m.starts_with("COP_")||m.starts_with("PART_")||m.starts_with("CONV_")||m.starts_with("VN_")||m.starts_with("INF_")||m.starts_with("ABILITY")){
        return unsupported("UNSUPPORTED_CLAUSE_OR_OPERATOR");
    }
    if rp=="VERB"&&fp=="VERB" {
        if !frames.contains(&root){return unsupported("UNSUPPORTED_FRAME");}
        if mids.len()!=2||mids[0]!="TAM_PAST"{return unsupported("UNSUPPORTED_VERB_PATTERN");}
        if let Some(p)=person(&mids[1],"AGR_"){return Ok((root,Some(Tag::Verb{person:p}),String::new()));}
        return unsupported("UNSUPPORTED_AGREEMENT");
    }
    if rp!=fp||!matches!(fp,"NOUN"|"PROPN"|"PRON"){return unsupported("UNSUPPORTED_POS");}
    let mut plural=false;let mut poss=None;let mut case_="Nom".to_owned();let mut phase=0;
    for m in &mids {
        if m=="NUMBER_PL" && phase==0 {plural=true;phase=1;}
        else if m.starts_with("POSS_")&&phase<2 {poss=person(m,"POSS_");if poss.is_none(){return unsupported("INVALID_POSSESSIVE");}phase=2;}
        else if m.starts_with("CASE_")&&phase<3 {
            case_=match m.as_str(){"CASE_ACC"=>"Acc","CASE_GEN"=>"Gen",_=>return unsupported("UNSUPPORTED_CASE")}.into();phase=3;
        }else{return unsupported("UNSUPPORTED_NOMINAL_PATTERN");}
    }
    let p=if fp=="PRON" {
        match root.as_str(){"ben"=>1,"sen"=>2,"biz"=>{plural=true;1},"siz"=>{plural=true;2},"o"=>3,"onlar"=>{plural=true;3},_=>return unsupported("UNSUPPORTED_PRONOUN")}
    }else{3};
    Ok((root,Some(Tag::Nominal{case_,person:Person{p,plural},poss}),String::new()))
}
fn read_tokens(input:&V,frames:&BTreeSet<String>)->io::Result<Vec<Token>>{
    let mut out=Vec::new();let mut previous=0;
    for v in arr(input.get("tokens"))? {
        let start=v.get("start").usize()?;let end=v.get("end").usize()?;
        if end<=start||start<previous{return Err(json::err("overlapping/unordered spans"));}
        previous=end;let raw=v.get("raw").string()?.to_owned();
        if raw.chars().count()!=end-start{return Err(json::err("Unicode span length"));}
        let mut candidates=BTreeMap::<String,Candidate>::new();
        for c in arr(v.get("candidates"))? {
            let key=c.get("key").string()?.to_owned();
            let score=c.get("score").clone();
            if let V::Number(x)=&score {if !x.parse::<f64>().map_err(|_|json::err("score"))?.is_finite(){return Err(json::err("nonfinite score"));}}
            else{return Err(json::err("numeric source score required"));}
            if let Some(old)=candidates.get(&key){if old.score!=score{return Err(json::err("duplicate key score mismatch"));}continue;}
            let(root,tag,reason)=classify(&key,frames)?;
            candidates.insert(key.clone(),Candidate{key,root,tag,reason,score});
        }
        out.push(Token{raw,start,end,candidates:candidates.into_values().collect(),complete:v.get("search_complete").boolean()});
    }
    Ok(out)
}
fn agrees(a:&Person,b:&Person)->bool{a.p==b.p&&(a.p==3||a.plural==b.plural)}
impl Search<'_>{
    fn spend(&mut self)->bool{
        if self.nodes>=self.cap{self.complete=false;return false;}
        self.nodes+=1;true
    }
    fn dfs(&mut self,i:usize){
        if !self.spend(){return;}
        if i==self.tokens.len(){self.leaf();return;}
        for j in 0..self.tokens[i].candidates.len(){
            if self.tokens[i].candidates[j].tag.is_none(){continue;}
            self.selected.push(j);self.dfs(i+1);self.selected.pop();
            if !self.complete{return;}
        }
    }
    fn leaf(&mut self){
        let mut verbs=Vec::new();let mut noms=Vec::new();let mut gens=Vec::new();
        for (i,&j) in self.selected.iter().enumerate(){
            match self.tokens[i].candidates[j].tag.as_ref().unwrap(){
                Tag::Verb{..}=>verbs.push(i),
                Tag::Nominal{case_,..}=>if case_=="Gen"{gens.push(i)}else{noms.push(i)},
            }
        }
        if verbs.len()!=1||noms.len()!=2||gens.len()>1{return;}
        let v=verbs[0];
        let vp=match self.tokens[v].candidates[self.selected[v]].tag.as_ref().unwrap(){Tag::Verb{person}=>person,_=>unreachable!()};
        for &sub in &noms {
            let obj=if noms[0]==sub{noms[1]}else{noms[0]};
            let st=self.tokens[sub].candidates[self.selected[sub]].tag.as_ref().unwrap();
            let ot=self.tokens[obj].candidates[self.selected[obj]].tag.as_ref().unwrap();
            let Tag::Nominal{case_:sc,person:sp,..}=st else{continue};
            let Tag::Nominal{case_:oc,..}=ot else{continue};
            if sc!="Nom"||oc!="Acc"||!agrees(sp,vp){continue;}
            let mut owners=vec![None];
            if let Some(&owner)=gens.first(){
                owners.clear();
                let Tag::Nominal{person:op,..}=self.tokens[owner].candidates[self.selected[owner]].tag.as_ref().unwrap() else{continue};
                for &head in &noms {
                    if let Some(Tag::Nominal{poss:Some(hp),..})=&self.tokens[head].candidates[self.selected[head]].tag {
                        if agrees(op,hp){owners.push(Some((owner,head)));}
                    }
                }
            }
            for owner in owners {
                let ans=Answer{verb:v,subject:sub,object:obj,root:self.tokens[v].candidates[self.selected[v]].root.clone(),owner};
                self.plans+=1;
                if !self.answers.contains_key(&ans){self.answers.insert(ans.clone(),self.witness(&ans));}
            }
        }
    }
    fn endpoint(&self,i:usize)->V{
        let t=&self.tokens[i];let c=&t.candidates[self.selected[i]];
        obj!("token":n(i),"start":n(t.start),"end":n(t.end),"raw":s(&t.raw),"candidate_key":s(&c.key),"source_score":c.score.clone(),"clause_id":n(0))
    }
    fn edge(&self,d:usize,h:usize,r:&str,rule:&str)->V{
        obj!("dependent":self.endpoint(d),"head":self.endpoint(h),"relation":s(r),"clause_id":n(0),"rule_id":s(rule))
    }
    fn witness(&self,a:&Answer)->V{
        let mut edges=vec![self.edge(a.subject,a.verb,"nsubj","G0_BOUND_PERSON"),self.edge(a.object,a.verb,"obj","G0_FRAME_CASE")];
        if let Some((d,h))=a.owner{edges.push(self.edge(d,h,"nmod:poss","G0_BOUND_POSSESSOR"));}
        obj!("bindings":V::Array((0..self.tokens.len()).map(|i|self.endpoint(i)).collect()),"edges":V::Array(edges),
             "predicate":n(a.verb),"predicate_root":s(&a.root),"subject":n(a.subject),"object":n(a.object),
             "possessor":a.owner.map_or(V::Null,|(d,_)|n(d)),"possessed":a.owner.map_or(V::Null,|(_,h)|n(h)))
    }
}
fn complete_surface(raw:&str,tokens:&[Token])->bool{
    let chars:Vec<char>=raw.chars().collect();let mut previous=0;
    for (i,t) in tokens.iter().enumerate(){
        if t.end>chars.len()||t.raw.chars().any(char::is_whitespace)||(i>0&&t.start==previous)||chars[previous..t.start].iter().any(|c|!c.is_whitespace()){return false;}
        previous=t.end;
    }
    let rest:String=chars[previous..].iter().collect();
    let rest=rest.trim();rest.is_empty()||rest=="."
}
pub fn solve(input:&V,frames:&BTreeSet<String>)->io::Result<V>{
    let tokens=read_tokens(input,frames)?;
    let raw=input.get("raw").string()?;
    for t in &tokens {if raw.chars().skip(t.start).take(t.end-t.start).collect::<String>()!=t.raw{return Err(json::err("raw/token mismatch"));}}
    let cap=if input.has("node_budget"){input.get("node_budget").usize()?}else{200000};
    if cap>2000000{return Err(json::err("node budget exceeds experiment bound"));}
    let mut excluded=Vec::new();
    for(i,t)in tokens.iter().enumerate(){for c in &t.candidates{if c.tag.is_none(){excluded.push(obj!("token":n(i),"candidate_key":s(&c.key),"reason":s(&c.reason)));}}}
    let structural=input.get("surface_supported").boolean()&&complete_surface(raw,&tokens)&&matches!(tokens.len(),3|4);
    let upstream=tokens.iter().all(|t|t.complete);
    let mut search=Search{tokens:&tokens,cap,nodes:0,complete:true,plans:0,answers:BTreeMap::new(),selected:Vec::new()};
    if structural {search.dfs(0);}
    let status=if !structural{"OUT_OF_SCOPE"}else if !upstream||!search.complete{"INCOMPLETE"}else if search.plans==0{"NO_G0_PLAN"}else if search.answers.len()==1{"G0_CONSENSUS"}else{"G0_AMBIGUOUS"};
    let consensus=status=="G0_CONSENSUS";
    Ok(obj!("version":s("P128-EXACT-BOUND-YONT-G0-1"),"status":s(status),
       "enumeration_complete":V::Bool(structural&&search.complete),"candidate_generation_complete":V::Bool(upstream),
       "grammar_scope":s("CONDITIONAL_G0_CANDIDATE_INVENTORY"),"candidate_source":input.get("candidate_source").clone(),
       "claim_scope":s("Only predicate lemma and overt syntactic subject/object/possessor links; not full sentence meaning"),
       "predicate_polarity":s("affirmative under G0 assumptions"),
       "natural_language_correctness_certified":V::Bool(false),"baseline_override_allowed":V::Bool(false),
       "all_scores_ignored_for_consensus":V::Bool(true),"plan_count":n(search.plans),"answer_count":n(search.answers.len()),
       "nodes_visited":n(search.nodes),"node_budget":n(cap),"tokens":input.get("tokens").clone(),
       "excluded_candidate_hypotheses":V::Array(excluded),"answers":V::Array(search.answers.values().cloned().collect()),
       "candidate_assignment_consensus_computed":V::Bool(false),
       "representative_witness_only":V::Bool(true),"implicit_possessors_resolved":V::Bool(false),
       "conditional_role_answer":if consensus{
           let a=search.answers.keys().next().unwrap();
           obj!("predicate":n(a.verb),"predicate_root":s(&a.root),"subject":n(a.subject),"object":n(a.object),
             "possessor":a.owner.map_or(V::Null,|(d,_)|n(d)),"possessed":a.owner.map_or(V::Null,|(_,h)|n(h)))
       }else{V::Null},
       "representative_witness":if consensus{search.answers.values().next().unwrap().clone()}else{V::Null},
       "assumptions":V::Array(vec![s("One complete affirmative active past clause; explicit Nom subject and Acc object"),
          s("Optional one GEN possessor; person and first/second number agreement; only declared nominal/verb patterns"),
          s("Frame source is non-exhaustive assistant-authored research metadata"),
          s("Consensus is not proof that the actual intended interpretation is in the inventory")])
    ))
}
pub fn from_audit(analysis:&V,trace:&V,budget:usize)->io::Result<V>{
    let raw=analysis.get("raw").string()?;
    let spans=arr(analysis.get("spans"))?;let audit=arr(trace)?;
    let mut ai=0;let mut tokens=Vec::new();let mut surface_supported=true;let mut terminals=0;
    for span in spans {
        let text=span.get("raw").string()?;
        if ai<audit.len() && audit[ai].get("raw").string()?==text {
            let row=&audit[ai];ai+=1;
            let scores=row.get("scores");let mut cs=Vec::new();
            for path in arr(row.get("candidates").get("paths"))? {
                let key=path.get("key").string()?;let sc=arr(scores.get(key))?;
                if sc.len()!=3{return Err(json::err("native score triple"));}
                cs.push(obj!("key":s(key),"score":sc[0].clone()));
            }
            tokens.push(obj!("start":span.get("start").clone(),"end":span.get("end").clone(),"raw":s(text),
                "search_complete":row.get("candidates").get("search_complete").clone(),"candidates":V::Array(cs)));
        }else if text.chars().all(char::is_whitespace) {} else if text=="." && span.get("end").usize()?==raw.trim_end().chars().count() {terminals+=1;}
        else {surface_supported=false;}
    }
    if ai!=audit.len(){return Err(json::err("unmatched audit spans"));}
    surface_supported &= terminals<=1;
    Ok(obj!("raw":s(raw),"tokens":V::Array(tokens),"surface_supported":V::Bool(surface_supported),"node_budget":n(budget),
        "candidate_source":s("All P119 proposals; not limited to A2-accepted paths")))
}
