//! P112 diagnostic scopes only: no heap allocation per span/event; active only under ROOT.
use std::{cell::RefCell,time::Instant,marker::PhantomData,rc::Rc};
use crate::json::{V,n,s};
pub const ROOT:usize=0;
pub const PREPARED_CACHE:usize=1;
pub const CANDIDATE_CACHE:usize=2;
pub const SERIALIZED_SCAN:usize=3;
pub const SERIALIZED_PARSE:usize=4;
pub const PROVIDER:usize=5;
pub const SEARCH_API:usize=6;
pub const SEED_FETCH:usize=7;
pub const ANALYSIS_RECORD_BUILD:usize=8;
pub const SEARCH_OUTPUT_JSON:usize=9;
pub const SEARCH_STATS_JSON:usize=10;
pub const PROVIDER_SEARCH_PARSE:usize=11;
pub const ANNOTATION:usize=12;
pub const ANNOTATION_LOOKUP:usize=13;
pub const ANNOTATION_PARSE:usize=14;
pub const PROJECT_PATHS:usize=15;
pub const PROVIDER_FILTER:usize=16;
pub const REPLAY_API:usize=17;
pub const REPLAY_OUTPUT_JSON:usize=18;
pub const REPLAY_PARSE:usize=19;
pub const CACHE_ADMISSION:usize=20;
pub const CACHE_DUMP:usize=21;
pub const SEARCH_RAW_JSON:usize=22;
pub const SEARCH_PREFILTER:usize=23;
pub const SEARCH_SEED_ALLOWED:usize=24;
pub const SEARCH_INITIAL_STATE:usize=25;
pub const SEARCH_STATE_VISIT:usize=26;
pub const SEARCH_FINAL_CHECK:usize=27;
pub const SEARCH_RULE_LOOP:usize=28;
pub const SEARCH_CHILDREN_PUSH:usize=29;
pub const SEARCH_FOUND_INSERT:usize=30;
pub const SEARCH_RESULT_SORT:usize=31;
pub const N:usize=32;
pub const C:usize=25;
pub const LABELS:[&str;N]=["ROOT", "PREPARED_CACHE", "CANDIDATE_CACHE", "SERIALIZED_SCAN", "SERIALIZED_PARSE", "PROVIDER", "SEARCH_API", "SEED_FETCH", "ANALYSIS_RECORD_BUILD", "SEARCH_OUTPUT_JSON", "SEARCH_STATS_JSON", "PROVIDER_SEARCH_PARSE", "ANNOTATION", "ANNOTATION_LOOKUP", "ANNOTATION_PARSE", "PROJECT_PATHS", "PROVIDER_FILTER", "REPLAY_API", "REPLAY_OUTPUT_JSON", "REPLAY_PARSE", "CACHE_ADMISSION", "CACHE_DUMP", "SEARCH_RAW_JSON", "SEARCH_PREFILTER", "SEARCH_SEED_ALLOWED", "SEARCH_INITIAL_STATE", "SEARCH_STATE_VISIT", "SEARCH_FINAL_CHECK", "SEARCH_RULE_LOOP", "SEARCH_CHILDREN_PUSH", "SEARCH_FOUND_INSERT", "SEARCH_RESULT_SORT"];
pub const COUNTERS:[&str;C]=["prepared_fast_hits", "serialized_hits", "provider_misses", "cache_insertions", "cache_evictions", "oversize_skips", "native_analyses", "hypotheses_before_filter", "final_paths", "search_seed_entries", "search_allowed_entries", "search_visited", "search_expansions", "search_replay_steps", "search_analyses", "search_rule_attempts", "search_rule_passes", "replay_seed_entries", "replay_allowed_entries", "replay_visited", "replay_expansions", "replay_replay_steps", "replay_analyses", "replay_rule_attempts", "replay_rule_passes"];
pub const E_PREPARED_FAST_HITS:usize=0;
pub const E_SERIALIZED_HITS:usize=1;
pub const E_PROVIDER_MISSES:usize=2;
pub const E_CACHE_INSERTIONS:usize=3;
pub const E_CACHE_EVICTIONS:usize=4;
pub const E_OVERSIZE_SKIPS:usize=5;
pub const E_NATIVE_ANALYSES:usize=6;
pub const E_HYPOTHESES_BEFORE_FILTER:usize=7;
pub const E_FINAL_PATHS:usize=8;
pub const E_SEARCH_SEED_ENTRIES:usize=9;
pub const E_SEARCH_ALLOWED_ENTRIES:usize=10;
pub const E_SEARCH_VISITED:usize=11;
pub const E_SEARCH_EXPANSIONS:usize=12;
pub const E_SEARCH_REPLAY_STEPS:usize=13;
pub const E_SEARCH_ANALYSES:usize=14;
pub const E_SEARCH_RULE_ATTEMPTS:usize=15;
pub const E_SEARCH_RULE_PASSES:usize=16;
pub const E_REPLAY_SEED_ENTRIES:usize=17;
pub const E_REPLAY_ALLOWED_ENTRIES:usize=18;
pub const E_REPLAY_VISITED:usize=19;
pub const E_REPLAY_EXPANSIONS:usize=20;
pub const E_REPLAY_REPLAY_STEPS:usize=21;
pub const E_REPLAY_ANALYSES:usize=22;
pub const E_REPLAY_RULE_ATTEMPTS:usize=23;
pub const E_REPLAY_RULE_PASSES:usize=24;
#[derive(Clone,Copy,Default,Debug,PartialEq)]
struct Metric{calls:u64,inclusive:u64,own:u64}
#[derive(Clone,Copy,Default)]
struct Frame{id:usize,start:u64,child:u64}
struct State{epoch:Instant,depth:usize,max_depth:usize,stack:[Frame;32],metrics:[Metric;N],events:[u64;C]}
impl State{
 fn new()->Self{Self{epoch:Instant::now(),depth:0,max_depth:0,stack:[Frame::default();32],metrics:[Metric::default();N],events:[0;C]}}
 fn now(&self)->u64{self.epoch.elapsed().as_nanos().try_into().expect("P112 clock overflow")}
 fn enter_at(&mut self,id:usize,t:u64)->bool{
  assert!(id<N);if self.depth==0&&id!=ROOT{return false;}
  assert!(id!=ROOT||self.depth==0,"P112 nested root");assert!(self.depth<self.stack.len(),"P112 stack overflow");
  self.stack[self.depth]=Frame{id,start:t,child:0};self.depth+=1;self.max_depth=self.max_depth.max(self.depth);true
 }
 fn leave_at(&mut self,id:usize,t:u64){
  assert!(self.depth>0);let f=self.stack[self.depth-1];assert_eq!(f.id,id,"P112 stack order");
  let inclusive=t.checked_sub(f.start).expect("P112 reversed time");
  let own=inclusive.checked_sub(f.child).expect("P112 children exceed parent");
  self.depth-=1;let m=&mut self.metrics[id];m.calls=m.calls.checked_add(1).unwrap();
  m.inclusive=m.inclusive.checked_add(inclusive).unwrap();m.own=m.own.checked_add(own).unwrap();
  if self.depth>0{let p=&mut self.stack[self.depth-1];p.child=p.child.checked_add(inclusive).unwrap();}
 }
 fn clear(&mut self){assert_eq!(self.depth,0,"P112 active reset");self.metrics=[Metric::default();N];self.events=[0;C];self.max_depth=0;}
}
thread_local!{static STATE:RefCell<State>=RefCell::new(State::new());}
pub struct Span{id:usize,active:bool,depth:usize,_thread:PhantomData<Rc<()>>}
impl Span{
 pub fn enter(id:usize)->Self{let(active,depth)=STATE.with(|s|{let mut s=s.borrow_mut();let t=s.now();let active=s.enter_at(id,t);(active,s.depth)});Self{id,active,depth,_thread:PhantomData}}
}
impl Drop for Span{fn drop(&mut self){if self.active{STATE.with(|s|{let mut s=s.borrow_mut();assert_eq!(s.depth,self.depth,"P112 span depth order");let t=s.now();s.leave_at(self.id,t);});}}}
pub fn event(id:usize,value:u64){STATE.with(|s|{let mut s=s.borrow_mut();if s.depth>0{s.events[id]=s.events[id].checked_add(value).unwrap();}});}
pub fn search_stats(v:[u64;8]){
 STATE.with(|s|{let mut s=s.borrow_mut();if s.depth==0{return;}
  let replay=s.stack[..s.depth].iter().any(|f|f.id==REPLAY_API);
  assert!(replay||s.stack[..s.depth].iter().any(|f|f.id==SEARCH_API));
  let offset=if replay{E_REPLAY_SEED_ENTRIES}else{E_SEARCH_SEED_ENTRIES};
  for(i,x)in v.into_iter().enumerate(){s.events[offset+i]=s.events[offset+i].checked_add(x).unwrap();}
 });
}
pub fn reset(){STATE.with(|s|s.borrow_mut().clear());}
pub fn snapshot()->V{
 let(metrics,events,max_depth)=STATE.with(|s|{let s=s.borrow();assert_eq!(s.depth,0,"P112 active snapshot");(s.metrics,s.events,s.max_depth)});
 let total:u64=metrics.iter().map(|m|m.own).sum();assert_eq!(total,metrics[ROOT].inclusive,"P112 self accounting");
 crate::obj!("scopes":V::Array(metrics.iter().enumerate().map(|(i,m)|crate::obj!("label":s(LABELS[i]),"calls":n(m.calls as usize),"inclusive_ns":n(m.inclusive as usize),"self_ns":n(m.own as usize))).collect()),
 "counters":V::Object(events.iter().enumerate().map(|(i,v)|(COUNTERS[i].into(),n(*v as usize))).collect()),"max_depth":n(max_depth),"self_total_ns":n(total as usize),"state_bytes":n(std::mem::size_of::<State>()))
}
#[cfg(test)]mod tests{
 use super::*;
 #[test]fn nesting_repetition_and_reset(){
  let mut s=State::new();assert!(!s.enter_at(SEARCH_API,0));s.enter_at(ROOT,0);
  s.enter_at(PROVIDER,10);s.enter_at(SEARCH_API,20);s.enter_at(SEARCH_API,25);s.leave_at(SEARCH_API,30);s.leave_at(SEARCH_API,40);s.leave_at(PROVIDER,70);
  s.enter_at(PREPARED_CACHE,80);s.leave_at(PREPARED_CACHE,90);s.leave_at(ROOT,100);
  assert_eq!(s.metrics[ROOT],Metric{calls:1,inclusive:100,own:30});
  assert_eq!(s.metrics[PROVIDER],Metric{calls:1,inclusive:60,own:40});
  assert_eq!(s.metrics[SEARCH_API],Metric{calls:2,inclusive:25,own:20});
  assert_eq!(s.metrics.iter().map(|m|m.own).sum::<u64>(),100);
  s.clear();assert!(s.metrics.iter().all(|x|*x==Metric::default()));assert_eq!(s.max_depth,0);
 }
 #[test]fn raii_early_returns(){
  fn none()->Option<()>{let _s=Span::enter(PREPARED_CACHE);None::<()>?;Some(())}
  fn error()->Result<(),()>{let _s=Span::enter(PROVIDER);Err(())?;Ok(())}
  reset();{let _s=Span::enter(ROOT);assert!(none().is_none());assert!(error().is_err());}
  STATE.with(|s|{let s=s.borrow();assert_eq!(s.depth,0);assert_eq!(s.metrics[ROOT].calls,1);assert_eq!(s.metrics[PREPARED_CACHE].calls,1);assert_eq!(s.metrics[PROVIDER].calls,1);});
  snapshot();reset();{let _inactive=Span::enter(PROVIDER);}STATE.with(|s|assert_eq!(s.borrow().metrics[PROVIDER].calls,0));
 }

 #[test]fn search_visit_continue_break_and_child(){
  reset();{
   let _root=Span::enter(ROOT);let _search=Span::enter(SEARCH_API);
   for i in 0..3{
    let visit=Span::enter(SEARCH_STATE_VISIT);
    if i==0{continue;}if i==2{break;}drop(visit);
    let _rules=Span::enter(SEARCH_RULE_LOOP);let _children=Span::enter(SEARCH_CHILDREN_PUSH);
   }
  }
  STATE.with(|s|{let s=s.borrow();assert_eq!(s.depth,0);assert_eq!(s.metrics[SEARCH_STATE_VISIT].calls,3);assert_eq!(s.metrics[SEARCH_RULE_LOOP].calls,1);assert_eq!(s.metrics[SEARCH_CHILDREN_PUSH].calls,1);});
  snapshot();reset();
 }
 #[test]#[should_panic(expected="P112 active reset")]fn reset_rejects_active(){let mut s=State::new();s.enter_at(ROOT,0);s.clear();}
 #[test]#[should_panic(expected="P112 stack order")]fn rejects_wrong_order(){let mut s=State::new();s.enter_at(ROOT,0);s.enter_at(PROVIDER,1);s.leave_at(ROOT,10);}
 #[test]#[should_panic(expected="P112 children exceed parent")]fn rejects_negative_self(){let mut s=State::new();s.enter_at(ROOT,0);s.enter_at(PROVIDER,1);s.leave_at(PROVIDER,10);s.leave_at(ROOT,5);}
}
