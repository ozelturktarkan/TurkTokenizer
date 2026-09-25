use std::io::{self,Read,Write};
use crate::wire::*;
#[derive(Clone,Debug,PartialEq,Eq,Hash)]
pub enum Val {Null,Str(String),Bool(bool),Set(Vec<String>),List(Vec<Val>),Int(i64)}
impl Val {
 pub fn s(s:&str)->Self{Self::Str(s.into())}
 pub fn truth(&self)->bool{match self{Self::Null=>false,Self::Bool(x)=>*x,Self::Str(x)=>!x.is_empty(),Self::Set(x)=>!x.is_empty(),Self::List(x)=>!x.is_empty(),Self::Int(x)=>*x!=0}}
 pub fn read<R:Read>(r:&mut R)->io::Result<Self>{Ok(match u32_in(r)?{
  0=>Self::Null,1=>Self::Str(text_in(r)?),2=>Self::Bool(u32_in(r)?!=0),
  3=>{let n=count(r,1024)?;let mut v=Vec::new();for _ in 0..n{v.push(text_in(r)?);}v.sort();v.dedup();Self::Set(v)},
  4=>{let n=count(r,1024)?;let mut v=Vec::new();for _ in 0..n{v.push(Self::read(r)?);}Self::List(v)},
  5=>{let mut a=[0;8];r.read_exact(&mut a)?;Self::Int(i64::from_le_bytes(a))},
  _=>return Err(io::Error::other("value tag"))
 })}
 pub fn write<W:Write>(&self,w:&mut W)->io::Result<()>{match self{
  Self::Null=>u32_out(w,0)?,Self::Str(x)=>{u32_out(w,1)?;text_out(w,x)?},
  Self::Bool(x)=>{u32_out(w,2)?;u32_out(w,*x as u32)?},
  Self::Set(x)=>{u32_out(w,3)?;u32_out(w,x.len()as u32)?;for a in x{text_out(w,a)?}},
  Self::List(x)=>{u32_out(w,4)?;u32_out(w,x.len()as u32)?;for a in x{a.write(w)?}},
  Self::Int(x)=>{u32_out(w,5)?;w.write_all(&x.to_le_bytes())?}
 }Ok(())}
}
pub fn count<R:Read>(r:&mut R,max:u32)->io::Result<usize>{let n=u32_in(r)?;if n>max{return Err(io::Error::other("rules batch count"));}Ok(n as usize)}
pub type Ctx=Vec<(std::borrow::Cow<'static,str>,Val)>;
pub fn get<'a>(c:&'a Ctx,key:&str)->Option<&'a Val>{c.iter().find(|(k,_)|k.as_ref()==key).map(|(_,v)|v)}
pub fn hasstr(c:&Ctx,key:&str,s:&str)->bool{matches!(get(c,key),Some(Val::Str(v))if v==s)}
pub fn put(c:&mut Ctx,key:&str,v:Val){if let Some((_,old))=c.iter_mut().find(|(k,_)|k.as_ref()==key){*old=v;}else{c.push((key.to_owned().into(),v));}}
pub fn ctx_read<R:Read>(r:&mut R)->io::Result<Ctx>{let n=count(r,1024)?;let mut c=Vec::new();for _ in 0..n{let k=text_in(r)?;let v=Val::read(r)?;c.push((k.into(),v));}Ok(c)}
pub fn ctx_write<W:Write>(c:&Ctx,w:&mut W)->io::Result<()>{u32_out(w,c.len()as u32)?;for(k,v)in c{text_out(w,k)?;v.write(w)?;}Ok(())}
pub fn eq(a:&Val,b:&Val)->bool{match(a,b){(Val::Bool(x),Val::Int(y))|(Val::Int(y),Val::Bool(x))=>*x as i64==*y,_=>a==b}}
pub fn contains(container:&Val,item:&Val)->io::Result<bool>{Ok(match container{
 Val::List(xs)=>xs.iter().any(|v|eq(v,item)),
 Val::Set(xs)=>if let Val::Str(s)=item{xs.contains(s)}else{false},
 Val::Str(s)=>if let Val::Str(x)=item{s.contains(x)}else{return Err(io::Error::other("non-string substring operand"));},
 _=>return Err(io::Error::other("non-container predicate operand"))
})}
pub fn predicate(field:&str,op:&str,value:&Val,c:&Ctx)->io::Result<Option<bool>>{
 let Some(x)=get(c,field)else{return Ok(None)};
 Ok(Some(match op{"eq"=>eq(x,value),"ne"=>!eq(x,value),"in"=>contains(value,x)?,"not_in"=>!contains(value,x)?,"contains"=>contains(x,value)?,_=>return Err(io::Error::other("unknown predicate operation"))}))
}
#[derive(Clone,Debug)]
pub struct Out {pub pos:String,pub phase:String,pub feats:Ctx,pub par:String,pub num:String,pub poss:String,pub cop:u32,pub deriv:u32}
impl Out {
 pub fn write<W:Write>(&self,w:&mut W)->io::Result<()>{text_out(w,&self.pos)?;text_out(w,&self.phase)?;ctx_write(&self.feats,w)?;for s in [&self.par,&self.num,&self.poss]{text_out(w,s)?;}u32_out(w,self.cop)?;u32_out(w,self.deriv)}
}
#[derive(Clone,Debug)]
pub struct Node {pub surface:String,pub pos:String,pub phase:String,pub ids:Vec<usize>,pub mids:Vec<String>,pub contexts:Vec<Ctx>,pub feats:Ctx,pub par:String,pub num:String,pub poss:String,pub cop:u32,pub deriv:u32}
impl Node {
 pub fn read<R:Read>(r:&mut R)->io::Result<Self>{
  let surface=text_in(r)?;let pos=text_in(r)?;let phase=text_in(r)?;
  let ni=count(r,1024)?;let mut ids=Vec::new();for _ in 0..ni{let id=u32_in(r)?as usize;if id>=crate::rule_data::ROWS.len(){return Err(io::Error::other("node row index"));}ids.push(id);}
  let nm=count(r,1024)?;let mut mids=Vec::new();for _ in 0..nm{mids.push(text_in(r)?);}
  let nc=count(r,1024)?;let mut contexts=Vec::new();for _ in 0..nc{contexts.push(ctx_read(r)?);}
  let feats=ctx_read(r)?;let par=text_in(r)?;let num=text_in(r)?;let poss=text_in(r)?;let cop=u32_in(r)?;let deriv=u32_in(r)?;
  Ok(Self{surface,pos,phase,ids,mids,contexts,feats,par,num,poss,cop,deriv})
 }
 pub fn out(&self)->Out{Out{pos:self.pos.clone(),phase:self.phase.clone(),feats:self.feats.clone(),par:self.par.clone(),num:self.num.clone(),poss:self.poss.clone(),cop:self.cop,deriv:self.deriv}}
 pub fn root(&self)->bool{self.ids.is_empty()}
 pub fn has(&self,mid:&str)->bool{self.mids.iter().any(|x|x==mid)}
 pub fn last(&self,mid:&str)->bool{self.mids.last().is_some_and(|x|x==mid)}
 pub fn surface_node(&self)->crate::surface::Node{crate::surface::Node{surface:self.surface.clone(),pos:self.pos.clone(),phase:self.phase.clone(),has_ids:!self.root(),mids:self.mids.clone()}}
}
pub fn outs_write<W:Write>(xs:&Option<Vec<Out>>,w:&mut W)->io::Result<()>{u32_out(w,xs.is_some()as u32)?;if let Some(xs)=xs{u32_out(w,xs.len()as u32)?;for x in xs{x.write(w)?;}}Ok(())}