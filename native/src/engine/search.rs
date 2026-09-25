use std::{io::{self,Read,Write},rc::Rc,collections::{BTreeMap,BTreeSet}};
use crate::{wire::*,rule_values::*,rule_data::*,rule_transition::{one,has},rule_context,surface,lexicon::{Lexeme,Store},rules,search_state::{State,SeenSet,Live},search_json as j,search_metadata as meta};
#[derive(Default)]
struct Stats{seed_entries:u64,allowed_entries:u64,visited:u64,expansions:u64,replay_steps:u64,final_checks:u64,max_stack:usize,max_seen:usize,fields:[u64;2],audit:rules::Audit,analyses:usize}
impl Stats{
 fn json(&self,live:&Live)->String{
#[cfg(candidate_profile)] let _p112_span=crate::candidate_profile::Span::enter(crate::candidate_profile::SEARCH_STATS_JSON);

#[cfg(candidate_profile)] crate::candidate_profile::search_stats([self.seed_entries,self.allowed_entries,self.visited,self.expansions,self.replay_steps,self.analyses as u64,self.audit[0],self.audit[9]]);

  format!("{{\"seed_entries\":{},\"allowed_entries\":{},\"visited_nodes\":{},\"expansions\":{},\"replay_steps\":{},\"final_checks\":{},\"max_stack\":{},\"max_seen\":{},\"max_live_histories\":{},\"live_histories_after\":{},\"context_fields_generated\":{},\"context_fields_retained\":{},\"analyses\":{},\"audit\":{}}}",
   self.seed_entries,self.allowed_entries,self.visited,self.expansions,self.replay_steps,self.final_checks,self.max_stack,self.max_seen,live.peak.get(),live.now.get(),self.fields[0],self.fields[1],self.analyses,j::array(self.audit.iter().map(u64::to_string)))
 }
}
fn initial(e:&Lexeme,cfg:&mut surface::Config)->io::Result<State>{
 let(n,f,poss)=surface::initial(cfg,e)?;
 Ok(State::initial(Node{surface:n.surface,pos:n.pos,phase:n.phase,ids:Vec::new(),mids:Vec::new(),contexts:Vec::new(),
  feats:f.into_iter().map(|(k,v)|(k.into(),Val::s(v))).collect(),par:String::new(),num:"Sing".into(),poss:poss.into(),cop:0,deriv:0}))
}
fn nominal(p:&str)->bool{one(p,&["NOUN","PROPN","PRON","NOMINALIZED"])}
fn default(c:&mut Ctx,k:&str,v:&str){if get(c,k).is_none(){put(c,k,Val::s(v));}}
fn normal(p:&str)->&str{match p{"NOMINALIZED"=>"NOUN","CCONJ"|"SCONJ"=>"CONJ",_=>p}}
struct Analysis{id:String,lemma:String,output:String,cost:f64,json:String}
fn analysis(s:&State,e:&Lexeme,target:&str)->Analysis{
#[cfg(candidate_profile)] let _p112_span=crate::candidate_profile::Span::enter(crate::candidate_profile::ANALYSIS_RECORD_BUILD);

 let path=s.lineage();let output=if &*s.pos=="NOMINALIZED"{"NOUN"}else{&s.pos};
 let mut f=(*s.feats).clone();if nominal(&s.pos)&&&*s.phase!="AGR"{default(&mut f,"Case","Nom");default(&mut f,"Number",&s.num);}
 if e.pos=="VERB"||&*s.pos=="VERB"{default(&mut f,"Polarity","Pos");}
 let id=j::id(&e.id,&s.pos,path.iter().map(|h|j::quote(ROWS[h.rid].id)),&s.feats);
 let derivation=j::id(&e.lemma,&s.pos,path.iter().map(|h|j::quote(&h.mid)),&s.feats);
 let cost=s.depth as f64*0.08+s.deriv as f64*0.18;
 let json=format!("{{\"lexeme_id\":{},\"lemma\":{},\"root_pos\":{},\"output_pos\":{},\"record_ids\":{},\"morpheme_ids\":{},\"features\":{},\"surface\":{},\"realization_trace\":{},\"registry_version\":{},\"source\":\"R5_REGISTRY_GRAPH\",\"cost\":{},\"analysis_id\":{},\"derivation_key\":{}}}",
  j::quote(&e.id),j::quote(&e.lemma),j::quote(&e.pos),j::quote(output),j::array(path.iter().map(|h|j::quote(ROWS[h.rid].id))),
  j::array(path.iter().map(|h|j::quote(&h.mid))),j::object(&f),j::quote(target),j::array(path.iter().map(|h|h.trace_json())),
  j::quote(meta::VERSION),j::float(cost),j::quote(&id),j::quote(&derivation));
 Analysis{id,lemma:e.lemma.clone(),output:output.into(),cost,json}
}
fn manifest(limits:[u32;3])->String{format!("{}{{\"nodes\":{},\"candidates\":{},\"steps\":{}}}{}",meta::MANIFEST_HEAD,limits[0],limits[1],limits[2],meta::MANIFEST_TAIL)}
fn raw_result(raw:&str,normalized:&str,reason:&str)->String{
#[cfg(candidate_profile)] let _p112_span=crate::candidate_profile::Span::enter(crate::candidate_profile::SEARCH_RAW_JSON);

 format!("{{\"raw\":{},\"normalized\":{},\"status\":\"RAW\",\"analyses\":[],\"search_complete\":true,\"reason\":{}}}",j::quote(raw),j::quote(normalized),j::quote(reason))
}
pub fn search(raw:&str,limits:[u32;3],lex:&mut Store,cfg:&mut surface::Config)->io::Result<(String,String)>{
#[cfg(candidate_profile)] let _p112_span=crate::candidate_profile::Span::enter(crate::candidate_profile::SEARCH_API);

 let normalized=crate::unicode::lower(raw).replace('’',"'");let quote=normalized.chars().position(|c|c=='\'').map_or(-1,|n|n as i64);
 let target=normalized.replace('\'',"");let mut stats=Stats::default();let live=Rc::new(Live::default());
 if normalized.chars().filter(|c|*c=='\'').count()>1||quote==0||quote==normalized.chars().count()as i64-1{
  return Ok((raw_result(raw,&normalized,"MULTIPLE_APOSTROPHES"),stats.json(&live)));
 }
 if target.is_empty()||!target.chars().all(|c|crate::text_props::flags(c)&1!=0){
  return Ok((raw_result(raw,&normalized,"NON_ALPHABETIC_OR_SEPARATE_TOKEN"),stats.json(&live)));
 }
 let mut node_slot=None;
 let possible=crate::p112_expr!(SEARCH_PREFILTER, crate::suffix_filter::mask(&target));let mut skipped=0u64;let mut checked=0u64;
 #[cfg(all(allowed_rules,not(suffix_oracle)))] let mut allowed=crate::allowed_rules::AllowedRules::new(&possible);
 let (_,seeds)=crate::p112_expr!(SEED_FETCH, lex.seeds(&target))?;stats.seed_entries=seeds.len()as u64;let mut found:BTreeMap<String,Analysis>=BTreeMap::new();let mut budget=false;
 for e in seeds{
  if !crate::p112_expr!(SEARCH_SEED_ALLOWED, lex.allowed(&e,raw,quote as u32))?{continue;}stats.allowed_entries+=1;
  let mut stack=vec![crate::p112_expr!(SEARCH_INITIAL_STATE, initial(&e,cfg))?];let mut seen=SeenSet::new();stats.max_stack=stats.max_stack.max(1);
  while let Some(s)=stack.pop(){
#[cfg(candidate_profile)] let _p115_visit=crate::candidate_profile::Span::enter(crate::candidate_profile::SEARCH_STATE_VISIT);
   if !seen.insert(s.seen()){continue;}stats.max_seen=stats.max_seen.max(seen.len());stats.visited+=1;
   if stats.visited>limits[0]as u64{budget=true;break;}
   let n=s.node_reuse(&mut node_slot);
#[cfg(candidate_profile)] drop(_p115_visit);
   if &*s.surface==target{
    stats.final_checks+=1;
    if crate::p112_expr!(SEARCH_FINAL_CHECK, rule_context::final_ok(&n))?{
     let a=analysis(&s,&e,&target);crate::p112_expr!(SEARCH_FOUND_INSERT, found.insert(a.id.clone(),a));
     if found.len()>=limits[1]as usize{budget=true;break;}
    }
   }
   if s.depth>=limits[2]as usize{if &*s.surface!=target{budget=true;}continue;}
   stats.expansions+=1;
#[cfg(candidate_profile)] let _p115_rules=crate::candidate_profile::Span::enter(crate::candidate_profile::SEARCH_RULE_LOOP);
let sn=n.surface_node();
   for cls in surface::classes(&sn,&e){
    if e.pos=="PROPN"&&s.depth==0&&quote<0&&!has(&e,"NoQuote")&&one(cls,&["hlE","ylE","vtE","bfE"]){continue;}
    #[cfg(any(not(allowed_rules),suffix_oracle))] {
    for rid in by_class(cls){for mid in ROWS[*rid].mids{
     if !possible[*rid]{
      skipped+=1;
      if cfg!(suffix_oracle){
       let mut discarded=[0;10];
       if rules::apply(&n,&e,&sn,*rid,mid,&target,lex,cfg,&mut discarded)?.is_some(){return Err(io::Error::other(format!("suffix prefilter suppressed a valid step: {raw} {} {mid}",ROWS[*rid].id)));}
       checked+=1;
      }
      continue;
     }

     if let Some(step)=rules::apply(&n,&e,&sn,*rid,mid,&target,lex,cfg,&mut stats.audit)?{
      crate::p112_expr!(SEARCH_CHILDREN_PUSH, stack.extend(s.children(step,&live,&mut stats.fields)));stats.max_stack=stats.max_stack.max(stack.len());
     }
    }}
    }
    #[cfg(all(allowed_rules,not(suffix_oracle)))] {
     let selected=allowed.class(cls);skipped+=selected.skipped;
     for &(rid,mid) in &selected.pairs {
      if let Some(step)=crate::p118_search_apply!(rules::apply(&n,&e,&sn,rid,mid,&target,lex,cfg,&mut stats.audit))?{
       crate::p112_expr!(SEARCH_CHILDREN_PUSH, stack.extend(s.children(step,&live,&mut stats.fields)));stats.max_stack=stats.max_stack.max(stack.len());
      }
     }
    }
   }
  }
  if budget{break;}
 }
 crate::suffix_filter::record(skipped,checked);
 let mut analyses:Vec<_>=found.into_values().collect();crate::p112_expr!(SEARCH_RESULT_SORT, analyses.sort_by(|a,b|a.cost.partial_cmp(&b.cost).unwrap().then(a.lemma.cmp(&b.lemma)).then(a.output.cmp(&b.output)).then(a.id.cmp(&b.id))));
 stats.analyses=analyses.len();let status=if analyses.is_empty(){"UNRESOLVED"}else{"ANALYZED"};
 let result=crate::p112_expr!(SEARCH_OUTPUT_JSON, format!("{{\"raw\":{},\"normalized\":{},\"status\":{},\"search_complete\":{},\"visited_nodes\":{},\"analyses\":{},\"ranking\":\"STRUCTURAL_COST_NOT_CONTEXTUAL_PROBABILITY\",\"manifest\":{}}}",
  j::quote(raw),j::quote(&normalized),j::quote(status),!budget,stats.visited,j::array(analyses.into_iter().map(|a|a.json)),manifest(limits)));
 debug_assert_eq!(live.now.get(),0);Ok((result,stats.json(&live)))
}
pub fn replay(raw:&str,id:&str,final_pos:&str,inherited:bool,ids:&[usize],mids:&[String],features:&Ctx,lex:&mut Store,cfg:&mut surface::Config)->io::Result<(String,String)>{
#[cfg(candidate_profile)] let _p112_span=crate::candidate_profile::Span::enter(crate::candidate_profile::REPLAY_API);

 let mut stats=Stats::default();let live=Rc::new(Live::default());
 let Some(entry)=lex.replay_entry(id)?else{return Ok(("[]".into(),stats.json(&live)));};
 let target=crate::unicode::lower(raw).replace('\'',"").replace('’',"");
 let root=normal(&entry.pos).to_owned();let inherited:Vec<(String,String)>=if inherited{vec![("POSS_3_SING".into(),"-".into())]}else{Vec::new()};
 let mut node_slot=None;
 let mut states=vec![(initial(&entry,cfg)?,root,inherited)];stats.max_stack=1;
 for (index,(&rid,mid)) in ids.iter().zip(mids).enumerate(){
  if rid>=ROWS.len()||!ROWS[rid].mids.contains(&mid.as_str()){drop(states);return Ok(("[]".into(),stats.json(&live)));}
  let row=&ROWS[rid];let mut updated=Vec::new();
  for (s,logical,events) in states{
   let n=s.node_reuse(&mut node_slot);let sn=n.surface_node();stats.replay_steps+=1;
   let Some(step)=rules::apply(&n,&entry,&sn,rid,mid,&target,lex,cfg,&mut stats.audit)?else{continue;};
   for nn in s.children(step,&live,&mut stats.fields){
    let out=normal(&nn.pos);let prefix=one(&logical,&["ADJ","NUM"])&&out=="NOUN"&&["NUMBER_","POSS_","CASE_"].iter().any(|p|mid.starts_with(p));
    let(logical_out,boundary)=if mid.starts_with("COP_"){
     let v=if mid=="COP_WHILE"{"ADV"}else{"VERB"};(v,if logical!="VERB"||one(mid,&["COP_PRESENT","COP_GENERAL","COP_WHILE"]){v}else{"-"})
    }else if mid.starts_with("VOICE_")||one(row.class,&["ybE","bvE"]){("VERB","VERB")}
    else if mid.starts_with("PART_")||mid.starts_with("CONV_")||one(mid,&["INF_MAK","VN_MA","VN_IS"])||one(row.class,&["atE","ffE","fiE","fsE","ifE","iiE","isE","kcE","sdE","sfE","siE","syE","ypE","zyE"]){(out,out)}
    else{(if prefix{"NOUN"}else{logical.as_str()},"-")};
    let mut ev=events.clone();if prefix{ev.push(("ZERO_NOUN".into(),"NOUN".into()));}
    let functional=if mid=="ABILITY_NEG_BASE"&&mids.get(index+1).is_some_and(|m|m=="POLARITY_NEG"){"ABILITY"}else{mid};
    ev.push((functional.into(),boundary.into()));let logical_out=logical_out.to_owned();updated.push((nn,logical_out,ev));
   }
  }
  stats.max_stack=stats.max_stack.max(updated.len());states=updated;
 }
 let mut result:BTreeSet<Vec<(String,String)>>=BTreeSet::new();
 for(s,logical,events)in states{
  if &*s.surface!=target{continue;}stats.final_checks+=1;
  if !rule_context::final_ok(s.node_reuse(&mut node_slot))?||logical!=final_pos{continue;}
  let mut f=(*s.feats).clone();if nominal(&s.pos)&&&*s.phase!="AGR"{default(&mut f,"Case","Nom");default(&mut f,"Number",&s.num);}
  if f.iter().any(|(k,v)|get(features,k).is_some_and(|x|!crate::rule_values::eq(x,v))){continue;}
  result.insert(events);
 }
 stats.analyses=result.len();let json=crate::p112_expr!(REPLAY_OUTPUT_JSON, j::array(result.into_iter().map(|events|j::array(events.into_iter().map(|(m,p)|format!("[{},{}]",j::quote(&m),j::quote(&p)))))));
 debug_assert_eq!(live.now.get(),0);Ok((json,stats.json(&live)))
}
pub fn command<R:Read,W:Write>(cmd:u32,r:&mut R,w:&mut W,lex:&mut Store,cfg:&mut surface::Config)->io::Result<()>{
 match cmd{
  35=>{let raw=text_in(r)?;let limits=[u32_in(r)?,u32_in(r)?,u32_in(r)?];if limits[0]>20000||limits[1]>256||limits[2]>20{return Err(io::Error::other("frozen search limits"));}let(result,stats)=search(&raw,limits,lex,cfg)?;text_out(w,&result)?;text_out(w,&stats)?;},
  36=>{let raw=text_in(r)?;let id=text_in(r)?;let final_pos=text_in(r)?;let inherited=u32_in(r)?!=0;
   let ni=count(r,64)?;let mut ids=Vec::new();for _ in 0..ni{ids.push(u32_in(r)?as usize);}
   let nm=count(r,64)?;let mut mids=Vec::new();for _ in 0..nm{mids.push(text_in(r)?);}
   let features=ctx_read(r)?;let(result,stats)=replay(&raw,&id,&final_pos,inherited,&ids,&mids,&features,lex,cfg)?;text_out(w,&result)?;text_out(w,&stats)?;},
  37=>{let n=count(r,128)?;let mut xs=Vec::new();for _ in 0..n{xs.push(text_in(r)?);}
   for s in xs{text_out(w,&j::quote(&s))?;text_out(w,&j::sha256(s.as_bytes()))?;}},
  _=>return Err(io::Error::other("search command"))
 }w.flush()
}
