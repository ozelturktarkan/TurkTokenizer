use std::io::{self,Read,Write};
use crate::{wire::*,rule_values::*,rule_data::*,rule_transition::*,rule_context,lexicon::{Lexeme,Store},surface};
pub type Audit=[u64;10];
pub struct Step {pub rid:usize,pub mid:String,pub out:Vec<Out>,pub stem:String,pub trace:Vec<&'static str>,pub context:Ctx}
impl Step{fn write<W:Write>(&self,w:&mut W)->io::Result<()>{u32_out(w,self.rid as u32)?;text_out(w,&self.mid)?;u32_out(w,self.out.len()as u32)?;for o in &self.out{o.write(w)?;}text_out(w,&self.stem)?;u32_out(w,self.trace.len()as u32)?;for t in &self.trace{text_out(w,t)?;}ctx_write(&self.context,w)}}
fn pair<R:Read>(r:&mut R)->io::Result<(usize,String)>{let i=u32_in(r)?as usize;if i>=ROWS.len(){return Err(io::Error::other("row index"));}Ok((i,text_in(r)?))}
pub fn apply(n:&Node,e:&Lexeme,sn:&surface::Node,rid:usize,mid:&str,target:&str,lex:&mut Store,cfg:&mut surface::Config,a:&mut Audit)->io::Result<Option<Step>>{
 a[0]+=1;let Some(out)=crate::p118_expr!(TRANSITION,transition(n,e,&ROWS[rid],mid,lex))?else{a[1]+=1;crate::p118_end!(TRANSITION_NONE);return Ok(None)};
 if out.is_empty(){a[2]+=1;crate::p118_end!(TRANSITION_EMPTY);return Ok(None);}a[3]+=out.len()as u64;
 let row=&ROWS[rid];let sr=crate::p118_expr!(ROW_SURFACE,row.surface_row());let(stem,trace)=crate::p118_expr!(CHANGED,surface::changed(cfg,sn,e,&sr,mid))?;a[4]+=1;
 let text=crate::p118_expr!(TEXT,format!("{stem}{}",row.suffix()));
 if !crate::p118_expr!(PREFIX,surface::prefix(cfg,sn,e,&sr,mid,&text,target))?{crate::p118_end!(PREFIX_FALSE);return Ok(None);}a[5]+=1;
 if !crate::p118_expr!(NEXT_OK,rule_context::next_ok(n,row,mid))?{crate::p118_end!(NEXT_FALSE);return Ok(None);}a[6]+=1;
 if crate::p118_expr!(LICENSE_GUARD,row.exact()&&!crate::p118_license!(cfg.licensed(row.id,&n.surface,&text))?){crate::p118_end!(LICENSE_FALSE);return Ok(None);}a[7]+=1;
 let mut context=crate::p118_expr!(CONTEXT,rule_context::context(n,e,row,mid,&stem,target))?;a[8]+=1;
 if n.par=="IMP"&&one(row.id,&["ksE0049","ksE0050","ksE0051","ksE0052","ksE0053","ksE0054","ksE0055","ksE0056"]){ps(&mut context,"agreement_paradigm","IMP_POLITE");}
 if !crate::p118_expr!(LOCAL_CHECK,rule_context::check_record(row,&context,true))?.is_empty(){crate::p118_end!(RECORD_FALSE);return Ok(None);}a[9]+=1;
 crate::p118_expr!(STEP_BUILD,Ok(Some(Step{rid,mid:mid.into(),out,stem,trace,context})))
}
fn audit_out<W:Write>(a:&Audit,w:&mut W)->io::Result<()>{for n in a{w.write_all(&n.to_le_bytes())?;}Ok(())}
fn strings<W:Write>(w:&mut W,xs:&[String])->io::Result<()>{u32_out(w,xs.len()as u32)?;for x in xs{text_out(w,x)?;}Ok(())}
pub fn command<R:Read,W:Write>(cmd:u32,r:&mut R,w:&mut W,lex:&mut Store,cfg:&mut surface::Config)->io::Result<()>{
 match cmd{
  29=>{
   let node=Node::read(r)?;let e=Lexeme::read(r)?;let n=count(r,128)?;let mut pairs=Vec::new();for _ in 0..n{pairs.push(pair(r)?);}
   for(i,mid)in pairs{outs_write(&transition(&node,&e,&ROWS[i],&mid,lex)?,w)?;}
  },
  30=>{
   let node=Node::read(r)?;let e=Lexeme::read(r)?;let target=text_in(r)?;let n=count(r,128)?;let mut pairs=Vec::new();for _ in 0..n{let(i,mid)=pair(r)?;pairs.push((i,mid,text_in(r)?));}
   for(i,mid,stem)in pairs{ctx_write(&rule_context::context(&node,&e,&ROWS[i],&mid,&stem,&target)?,w)?;}
  },
  31=>{
   let mode=u32_in(r)?;let n=count(r,128)?;
   if mode==0{
    let mut xs=Vec::new();for _ in 0..n{xs.push((text_in(r)?,text_in(r)?,Val::read(r)?,ctx_read(r)?));}
    for(field,op,value,ctx)in xs{let v=predicate(&field,&op,&value,&ctx)?;u32_out(w,match v{None=>2,Some(false)=>0,Some(true)=>1})?;}
   }else if mode==1{
    let mut xs=Vec::new();for _ in 0..n{let i=u32_in(r)?as usize;if i>=ROWS.len(){return Err(io::Error::other("check row"));}xs.push((i,ctx_read(r)?));}
    for(i,ctx)in xs{strings(w,&rule_context::check_record(&ROWS[i],&ctx,false)?)?;u32_out(w,rule_context::check_record(&ROWS[i],&ctx,true)?.is_empty()as u32)?;}
   }else{return Err(io::Error::other("predicate mode"));}
  },
  32=>{
   let node=Node::read(r)?;let n=count(r,128)?;let mut pairs=Vec::new();for _ in 0..n{pairs.push(pair(r)?);}
   u32_out(w,rule_context::final_ok(&node)?as u32)?;
   for(i,mid)in pairs{u32_out(w,rule_context::next_ok(&node,&ROWS[i],&mid)?as u32)?;}
  },
  33|34=>{
   let node=Node::read(r)?;let e=Lexeme::read(r)?;let target=text_in(r)?;let sn=node.surface_node();let mut a=[0;10];let mut out=Vec::new();
   if cmd==33{
    let quote=u32_in(r)?;
    for cls in surface::classes(&sn,&e){
     if e.pos=="PROPN"&&node.root()&&quote==u32::MAX&&!has(&e,"NoQuote")&&one(cls,&["hlE","ylE","vtE","bfE"]){continue;}
     for i in by_class(cls){for mid in ROWS[*i].mids{if let Some(step)=apply(&node,&e,&sn,*i,mid,&target,lex,cfg,&mut a)?{out.push(step);}}}
    }
   }else{let(i,mid)=pair(r)?;if let Some(step)=apply(&node,&e,&sn,i,&mid,&target,lex,cfg,&mut a)?{out.push(step);}}
   audit_out(&a,w)?;u32_out(w,out.len()as u32)?;for step in out{step.write(w)?;}
  },
  _=>return Err(io::Error::other("rules command"))
 }w.flush()
}