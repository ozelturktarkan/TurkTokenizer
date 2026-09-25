//! Diagnostic-only sampling, explicitly entered only by search's apply call.
use std::{cell::{Cell,RefCell},time::Instant,io};
use crate::json::{V,n,s};
pub const N:usize=10;
pub const LABELS:[&str;N]=["TRANSITION","ROW_SURFACE","CHANGED","TEXT","PREFIX","NEXT_OK","LICENSE_GUARD","CONTEXT","LOCAL_CHECK","STEP_BUILD"];
pub const TRANSITION:usize=0;pub const ROW_SURFACE:usize=1;pub const CHANGED:usize=2;pub const TEXT:usize=3;pub const PREFIX:usize=4;
pub const NEXT_OK:usize=5;pub const LICENSE_GUARD:usize=6;pub const CONTEXT:usize=7;pub const LOCAL_CHECK:usize=8;pub const STEP_BUILD:usize=9;
pub const TRANSITION_NONE:usize=0;pub const TRANSITION_EMPTY:usize=1;pub const PREFIX_FALSE:usize=2;pub const NEXT_FALSE:usize=3;pub const LICENSE_FALSE:usize=4;pub const RECORD_FALSE:usize=5;
#[derive(Clone)]struct Data{seed:u64,key:u64,attempts:u64,samples:u64,xor:u64,root_ns:u64,calls:[u64;N],ns:[u64;N],terminals:[u64;9],errors:[u64;N+1],licensed:u64}
impl Data{const fn new(seed:u64)->Self{Self{seed,key:mix(seed),attempts:0,samples:0,xor:0,root_ns:0,calls:[0;N],ns:[0;N],terminals:[0;9],errors:[0;N+1],licensed:0}}}
thread_local!{
 static DATA:RefCell<Data>=const{RefCell::new(Data::new(118202600))};
 static ACTIVE:Cell<bool>=const{Cell::new(false)};
 static IN_STAGE:Cell<bool>=const{Cell::new(false)};
 static LAST:Cell<usize>=const{Cell::new(N)};
 static TERMINAL:Cell<usize>=const{Cell::new(8)};
}
pub const fn mix(mut z:u64)->u64{z=z.wrapping_add(0x9e3779b97f4a7c15);z=(z^(z>>30)).wrapping_mul(0xbf58476d1ce4e5b9);z=(z^(z>>27)).wrapping_mul(0x94d049bb133111eb);z^(z>>31)}
pub fn reset(seed:u64){assert!(!ACTIVE.with(Cell::get)&&!IN_STAGE.with(Cell::get));DATA.with(|d|*d.borrow_mut()=Data::new(seed));}
pub fn terminal(id:usize){if ACTIVE.with(Cell::get){assert!(id<6);TERMINAL.with(|c|{assert_eq!(c.get(),8);c.set(id)});}}
pub fn licensed(){if ACTIVE.with(Cell::get){DATA.with(|d|d.borrow_mut().licensed+=1);}}
pub struct Call{start:Option<Instant>,done:bool,_local:std::marker::PhantomData<std::rc::Rc<()>>}
impl Call{
 pub fn search()->Self{
  assert!(!ACTIVE.with(Cell::get),"nested sampled call");
  let take=DATA.with(|d|{let mut a=d.borrow_mut();let i=a.attempts;a.attempts+=1;let h=mix(a.key^i);if h&127==0{a.samples+=1;a.xor^=h;true}else{false}});
  if take{ACTIVE.with(|c|c.set(true));LAST.with(|c|c.set(N));TERMINAL.with(|c|c.set(8));}
  Self{start:take.then(Instant::now),done:false,_local:std::marker::PhantomData}
 }
 pub fn finish<T>(mut self,result:&io::Result<Option<T>>){
  if self.start.is_some(){
   let t=match result{Ok(Some(_))=>6,Ok(None)=>{let t=TERMINAL.with(Cell::get);assert!(t<6,"unclassified None");t},Err(_)=>7};
   DATA.with(|d|{let mut a=d.borrow_mut();a.terminals[t]+=1;if t==7{a.errors[LAST.with(Cell::get)]+=1;}});
  }
  self.done=true;
 }
}
impl Drop for Call{
 fn drop(&mut self){if let Some(start)=self.start{
  let ns=start.elapsed().as_nanos()as u64;assert!(!IN_STAGE.with(Cell::get));
  DATA.with(|d|{let mut a=d.borrow_mut();a.root_ns+=ns;if !self.done{a.terminals[8]+=1;}});
  ACTIVE.with(|c|c.set(false));
 }}
}
pub struct Stage{start:Option<Instant>,id:usize,_local:std::marker::PhantomData<std::rc::Rc<()>>}
impl Stage{pub fn enter(id:usize)->Self{
 let active=ACTIVE.with(Cell::get);
 if active{assert!(id<N);IN_STAGE.with(|c|{assert!(!c.get());c.set(true)});LAST.with(|c|c.set(id));DATA.with(|d|d.borrow_mut().calls[id]+=1);}
 Self{start:active.then(Instant::now),id,_local:std::marker::PhantomData}
}}
impl Drop for Stage{fn drop(&mut self){if let Some(t)=self.start{
 let ns=t.elapsed().as_nanos()as u64;DATA.with(|d|d.borrow_mut().ns[self.id]+=ns);IN_STAGE.with(|c|c.set(false));
}}}
pub fn snapshot()->V{
 assert!(!ACTIVE.with(Cell::get)&&!IN_STAGE.with(Cell::get));
 let a=DATA.with(|d|d.borrow().clone());let sum:u64=a.ns.iter().sum();assert!(sum<=a.root_ns);
 let arr=|xs:&[u64]|V::Array(xs.iter().map(|v|n(*v as usize)).collect());
 crate::obj!("seed":n(a.seed as usize),"attempts":n(a.attempts as usize),"samples":n(a.samples as usize),"selection_xor_hex":s(format!("{:016x}",a.xor)),"root_ns":n(a.root_ns as usize),"residual_ns":n((a.root_ns-sum)as usize),"stage_labels":V::Array(LABELS.iter().map(|x|s(*x)).collect()),"stage_calls":arr(&a.calls),"stage_ns":arr(&a.ns),"terminals":arr(&a.terminals),"error_stages":arr(&a.errors),"actual_licensed_calls":n(a.licensed as usize),"state_bytes":n(std::mem::size_of::<Data>()))
}
#[cfg(test)]mod tests{
 use super::*;
 #[test]fn deterministic_selection_and_no_outside_stage(){
  reset(118202600);{let _p=Stage::enter(NEXT_OK);}assert_eq!(DATA.with(|d|d.borrow().calls),[0;N]);
  let mut selected=0;let mut xor=0;
  for i in 0..100000{let h=mix(mix(118202600)^i);if h&127==0{selected+=1;xor^=h;}
   let call=Call::search();{let _p=Stage::enter(TRANSITION);}terminal(TRANSITION_NONE);call.finish(&Ok::<Option<()>,io::Error>(None));}
  let a=DATA.with(|d|d.borrow().clone());assert_eq!(a.attempts,100000);assert_eq!(a.samples,selected);assert_eq!(a.xor,xor);assert_eq!(a.terminals[0],selected);assert_eq!(a.calls[0],selected);snapshot();
 }
 fn selected_seed()->u64{(0..100000).find(|s|mix(mix(*s))&127==0).unwrap()}
 fn failing()->io::Result<Option<()>>{let _p=Stage::enter(NEXT_OK);Err(io::Error::other("expected"))?;Ok(Some(()))}
 #[test]fn errors_and_early_returns_close(){
  reset(selected_seed());let call=Call::search();let r=failing();call.finish(&r);
  let a=DATA.with(|d|d.borrow().clone());assert_eq!(a.terminals[7],1);assert_eq!(a.errors[NEXT_OK],1);snapshot();
  reset(selected_seed());let call=Call::search();{let _p=Stage::enter(PREFIX);}terminal(PREFIX_FALSE);call.finish(&Ok::<Option<()>,io::Error>(None));snapshot();
  reset(selected_seed());let call=Call::search();{let _p=Stage::enter(STEP_BUILD);}call.finish(&Ok::<_,io::Error>(Some(())));assert_eq!(DATA.with(|d|d.borrow().terminals[6]),1);snapshot();
 }
 #[test]fn unfinished_call_is_visible(){reset(selected_seed());{let _call=Call::search();}assert_eq!(DATA.with(|d|d.borrow().terminals[8]),1);snapshot();}

 #[test]fn all_none_terminals_and_macro_inner_error(){
  for id in 0..6{reset(selected_seed());let call=Call::search();terminal(id);call.finish(&Ok::<Option<()>,io::Error>(None));assert_eq!(DATA.with(|d|d.borrow().terminals[id]),1);snapshot();}
  fn fail()->io::Result<Option<()>>{
   if crate::p118_expr!(LICENSE_GUARD,true&&!crate::p118_license!(Err::<bool,io::Error>(io::Error::other("expected")))?){return Ok(None)}Ok(Some(()))
  }
  reset(selected_seed());let call=Call::search();let r=fail();call.finish(&r);
  assert_eq!(DATA.with(|d|d.borrow().errors[LICENSE_GUARD]),1);assert_eq!(DATA.with(|d|d.borrow().licensed),1);snapshot();
 }
 #[test]fn adjacent_seeds_do_not_permute_small_ordinal_blocks(){
  let seeds=[118202600,118202631,118203609];
  let mut counts=[0;3];let mut overlap=0;
  for i in 0..131072{let hit=seeds.map(|s|mix(mix(s)^i)&127==0);for k in 0..3{counts[k]+=hit[k]as usize;}overlap+=(hit[0]&&hit[1])as usize;}
  assert!(counts.iter().all(|n|*n>800&&*n<1300));assert!(overlap<40);
  let block=|seed| (0..512).filter(|i|mix(mix(seed)^i)&127==0).count();
  assert_ne!((0..16).map(|b|block(seeds[0]+b)).collect::<Vec<_>>(),vec![block(seeds[0]);16]);
 }
 #[test]#[should_panic]fn reset_during_selected_call_rejected(){reset(selected_seed());let _call=Call::search();reset(1);}
}
