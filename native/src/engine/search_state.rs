use std::{rc::Rc,cell::Cell,collections::HashSet};
use crate::{rule_values::{Node,Out,Ctx},rule_data::{Row,ROWS},rules::Step,search_json as j};
#[derive(Default)]
pub struct Live {pub now:Cell<u64>,pub peak:Cell<u64>}
pub struct History{
 pub parent:Option<Rc<History>>,pub rid:usize,pub mid:String,pub ctx:Ctx,
 pub before:Rc<str>,pub stem:Rc<str>,pub after:Rc<str>,pub rules:Vec<&'static str>,live:Rc<Live>,
}
impl Drop for History{fn drop(&mut self){self.live.now.set(self.live.now.get()-1);}}
impl History{
 pub fn trace_json(&self)->String{
  format!("{{\"record_id\":{},\"morpheme_id\":{},\"before\":{},\"realized_stem\":{},\"suffix\":{},\"after\":{},\"rules\":{}}}",
   j::quote(ROWS[self.rid].id),j::quote(&self.mid),j::quote(&self.before),j::quote(&self.stem),j::quote(ROWS[self.rid].suffix()),j::quote(&self.after),j::array(self.rules.iter().map(|s|j::quote(s))))
 }
}
#[derive(Clone)]
pub struct State{
 pub surface:Rc<str>,pub pos:Rc<str>,pub phase:Rc<str>,pub history:Option<Rc<History>>,pub feats:Rc<Ctx>,
 pub par:Rc<str>,pub num:Rc<str>,pub poss:Rc<str>,pub cop:u32,pub deriv:u32,pub depth:usize,
}
#[derive(PartialEq,Eq,Hash)]
pub struct Seen{surface:Rc<str>,pos:Rc<str>,phase:Rc<str>,ids:Box<[u16]>,feats:Rc<Ctx>,par:Rc<str>}
impl State{
 pub fn initial(node:Node)->Self{
  let mut f=node.feats;f.sort_by(|a,b|a.0.cmp(&b.0));
  Self{surface:node.surface.into(),pos:node.pos.into(),phase:node.phase.into(),history:None,feats:Rc::new(f),par:node.par.into(),num:node.num.into(),poss:node.poss.into(),cop:node.cop,deriv:node.deriv,depth:0}
 }
 pub fn lineage(&self)->Vec<&History>{
  let mut out=Vec::with_capacity(self.depth);let mut h=self.history.as_deref();
  while let Some(x)=h{out.push(x);h=x.parent.as_deref();}out.reverse();out
 }
 pub fn node(&self)->Node{
  let path=self.lineage();Node{surface:self.surface.to_string(),pos:self.pos.to_string(),phase:self.phase.to_string(),
   ids:path.iter().map(|h|h.rid).collect(),mids:path.iter().map(|h|h.mid.clone()).collect(),contexts:path.iter().map(|h|h.ctx.clone()).collect(),
   feats:((*self.feats).clone()),par:self.par.to_string(),num:self.num.to_string(),poss:self.poss.to_string(),cop:self.cop,deriv:self.deriv}
 }
 // Scratch is owned by one search/replay invocation; no reference escapes it.
 pub fn node_reuse<'a>(&self,slot:&'a mut Option<Node>)->&'a Node{
  #[cfg(node_oracle)] let prior=slot.as_ref().map(|n|n.ids.len());
  match slot{
   Some(out)=>{
    for(dst,src)in [(&mut out.surface,self.surface.as_ref()),(&mut out.pos,self.pos.as_ref()),
     (&mut out.phase,self.phase.as_ref()),(&mut out.par,self.par.as_ref()),
     (&mut out.num,self.num.as_ref()),(&mut out.poss,self.poss.as_ref())]{
     dst.clear();dst.push_str(src);
    }
    let path=self.lineage();
    out.ids.clear();out.ids.extend(path.iter().map(|h|h.rid));
    out.mids.truncate(path.len());out.contexts.truncate(path.len());
    for(i,h)in path.iter().enumerate(){
     if let Some(mid)=out.mids.get_mut(i){mid.clone_from(&h.mid);}else{out.mids.push(h.mid.clone());}
     if let Some(ctx)=out.contexts.get_mut(i){ctx.clone_from(&h.ctx);}else{out.contexts.push(h.ctx.clone());}
    }
    out.feats.clone_from(self.feats.as_ref());
    out.cop=self.cop;out.deriv=self.deriv;
   },
   None=>*slot=Some(self.node()),
  }
  let out=slot.as_ref().unwrap();
  #[cfg(node_oracle)] {
   let expected=self.node();
   macro_rules! same {($($field:ident),+)=>{$(assert_eq!(out.$field,expected.$field,stringify!($field));)+}}
   same!(surface,pos,phase,ids,mids,contexts,feats,par,num,poss,cop,deriv);
   use std::sync::atomic::Ordering::Relaxed;
   NODE_CHECKS[0].fetch_add(1,Relaxed);
   if let Some(depth)=prior{
    NODE_CHECKS[1].fetch_add(1,Relaxed);
    if out.ids.len()>depth{NODE_CHECKS[2].fetch_add(1,Relaxed);}
    if out.ids.len()<depth{NODE_CHECKS[3].fetch_add(1,Relaxed);}
   }
  }
  out
 }
 pub fn seen(&self)->Seen{Seen{surface:self.surface.clone(),pos:self.pos.clone(),phase:self.phase.clone(),
  ids:self.lineage().iter().map(|h|h.rid as u16).collect(),feats:self.feats.clone(),par:self.par.clone()}}
 pub fn children(&self,step:Step,live:&Rc<Live>,fields:&mut[u64;2])->Vec<State>{
  let Step{rid,mid,out,stem,trace,mut context}=step;let row:&Row=&ROWS[rid];
  fields[0]+=context.len()as u64;
  // All history consumers are frozen: next/final record predicates and the first lexeme check.
  // The complete current-step context has already passed P78 local checks.
  context.retain(|(key,_)|key.as_ref()=="lexeme"||row.left.iter().chain(row.right.iter()).any(|c|c.field==key.as_ref()));
  fields[1]+=context.len()as u64;
  let after:Rc<str>=format!("{stem}{}",row.suffix()).into();let now=live.now.get()+1;live.now.set(now);live.peak.set(live.peak.get().max(now));
  let history=Rc::new(History{parent:self.history.clone(),rid,mid,ctx:context,before:self.surface.clone(),stem:stem.into(),after:after.clone(),rules:trace,live:live.clone()});
  out.into_iter().map(|Out{pos,phase,mut feats,par,num,poss,cop,deriv}|{
   feats.sort_by(|a,b|a.0.cmp(&b.0));
   State{surface:after.clone(),pos:pos.into(),phase:phase.into(),history:Some(history.clone()),feats:Rc::new(feats),
    par:par.into(),num:num.into(),poss:poss.into(),cop,deriv,depth:self.depth+1}
  }).collect()
 }
}
pub type SeenSet=HashSet<Seen>;

#[cfg(node_oracle)]
static NODE_CHECKS:[std::sync::atomic::AtomicU64;4]=[const{std::sync::atomic::AtomicU64::new(0)};4];
#[cfg(node_oracle)]
pub fn node_checks()->[u64;4]{NODE_CHECKS.each_ref().map(|x|x.load(std::sync::atomic::Ordering::Relaxed))}
