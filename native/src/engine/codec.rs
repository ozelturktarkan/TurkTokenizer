use crate::paged_file::PagedFile;
#[cfg(not(lookup_index))] use crate::tables::Table as Lookup;
#[cfg(lookup_index)] use crate::lookup_index::Lookup;
use std::io::{self,Read,Write,Seek,SeekFrom};
use std::path::Path;
use std::collections::BinaryHeap;
use std::cmp::Reverse;
use crate::wire::*;
#[path="bpe_data.rs"] mod bpe_data;
pub const COUNT:u32=345127;
pub struct Part{pub kind:String,pub key:String,pub surface:String}
pub fn parts_in<R:Read>(r:&mut R)->io::Result<Vec<Part>>{
 let n=u32_in(r)?;if n>100000{return Err(io::Error::other("parts bound"));}
 let mut parts=Vec::with_capacity(n as usize);
 for _ in 0..n{parts.push(Part{kind:text_in(r)?,key:text_in(r)?,surface:text_in(r)?});}Ok(parts)
}
pub struct Codec{surfaces:PagedFile,lookup:Lookup,length:u64}
impl Codec{
 pub fn open(dir:&Path)->io::Result<Self>{
  let mut surfaces=PagedFile::open(&dir.join("surfaces.bin"))?;let length=surfaces.len();
  let mut magic=[0;8];surfaces.read_exact(&mut magic)?;
  if &magic!=b"P74SUR1\0" || u64_in(&mut surfaces)?!=COUNT as u64{return Err(io::Error::other("surface header"));}
  Ok(Self{surfaces,lookup:Lookup::open(&dir.join("lookup.bin"))?,length})
 }
 pub fn surface(&mut self,id:u32)->io::Result<Option<Vec<u8>>>{
  if id>=COUNT{return Ok(None);}
  self.surfaces.seek(SeekFrom::Start(16+id as u64*8))?;
  let lo=u64_in(&mut self.surfaces)?;let hi=u64_in(&mut self.surfaces)?;
  if lo<16+(COUNT as u64+1)*8 || hi<lo || hi>self.length{return Err(io::Error::other("surface offset"));}
  self.surfaces.seek(SeekFrom::Start(lo))?;let mut bytes=vec![0;(hi-lo)as usize];self.surfaces.read_exact(&mut bytes)?;Ok(Some(bytes))
 }
 pub fn find(&mut self,key:&str)->io::Result<Option<u32>>{
  match self.lookup.get(key)?{None=>Ok(None),Some(b)=>{
   if b.len()!=4{return Err(io::Error::other("lookup ID length"));}
   let id=u32::from_le_bytes(b.try_into().unwrap());
   if id<8 || id>=COUNT{return Err(io::Error::other("lookup ID range"));}Ok(Some(id))
  }}
 }
 pub fn encodable(&mut self,parts:&[Part])->io::Result<bool>{
  for p in parts{if p.kind!="LAYOUT" && self.find(&format!("{}\0{}",p.kind,p.key))?.is_none(){return Ok(false);}}Ok(true)
 }
 pub fn decode(&mut self,ids:&[u32])->io::Result<Option<Vec<u8>>>{
  if ids.iter().any(|i|*i<8 || *i>=COUNT){return Ok(None);}
  let mut raw=Vec::new();for id in ids{raw.extend(self.surface(*id)?.unwrap());}Ok(Some(raw))
 }
 pub fn encode_path(&mut self,parts:&[Part],raw:&[u8])->io::Result<Result<Vec<u32>,u32>>{
  let mut ids=Vec::new();
  for p in parts{
   if p.kind=="LAYOUT"{ids.extend(encode(p.surface.as_bytes()));}
   else{match self.find(&format!("{}\0{}",p.kind,p.key))?{Some(i)=>ids.push(i),None=>return Ok(Err(1))}}
  }
  if self.decode(&ids)?.as_deref()!=Some(raw){return Ok(Err(2));}Ok(Ok(ids))
 }
}
type Edge=Reverse<(u32,usize,usize,u32,u32,u32)>;
fn push(i:usize,ids:&[u32],next:&[usize],live:&[bool],heap:&mut BinaryHeap<Edge>){
 if i>=ids.len() || !live[i]{return;}let j=next[i];if j>=ids.len(){return;}
 let pair=(ids[i],ids[j]);
 if let Ok(k)=bpe_data::RULES.binary_search_by(|r|(r.0,r.1).cmp(&pair)){
  let(_,_,rank,new)=bpe_data::RULES[k];heap.push(Reverse((rank,i,j,ids[i],ids[j],new)));
 }
}
pub fn encode(raw:&[u8])->Vec<u32>{
 let mut result=Vec::with_capacity(raw.len());
 for chunk in raw.chunks(256){
  let n=chunk.len();let mut ids:Vec<u32>=chunk.iter().map(|b|*b as u32).collect();
  let mut previous:Vec<usize>=(0..n).map(|i|i.wrapping_sub(1)).collect();let mut next:Vec<usize>=(1..=n).collect();let mut live=vec![true;n];
  let mut heap:BinaryHeap<Edge>=BinaryHeap::with_capacity(n*2);
  for i in 0..n{push(i,&ids,&next,&live,&mut heap);}
  while let Some(Reverse((_,i,j,a,b,new)))=heap.pop(){
   if !live[i] || !live[j] || next[i]!=j || ids[i]!=a || ids[j]!=b{continue;}
   ids[i]=new;live[j]=false;next[i]=next[j];if next[j]<n{previous[next[j]]=i;}
   push(previous[i],&ids,&next,&live,&mut heap);push(i,&ids,&next,&live,&mut heap);
  }
  for i in 0..n{if live[i]{result.push(ids[i]+8);}}
 }result
}
fn ids_in<R:Read>(r:&mut R)->io::Result<Vec<u32>>{
 let n=u32_in(r)?;if n>1000000{return Err(io::Error::other("ID input bound"));}
 (0..n).map(|_|u32_in(r)).collect()
}
fn ids_out<W:Write>(w:&mut W,ids:&[u32])->io::Result<()>{
 u32_out(w,ids.len()as u32)?;for i in ids{u32_out(w,*i)?;}Ok(())
}
pub fn command<R:Read,W:Write>(cmd:u32,r:&mut R,w:&mut W,codec:&mut Codec)->io::Result<()>{
 // Read entire bounded request before sending, preventing pipe deadlocks.
 match cmd{
  8=>{
   let n=u32_in(r)?;if n>4096{return Err(io::Error::other("BPE batch bound"));}
   let rows:Vec<Vec<u8>>=(0..n).map(|_|bytes_in(r)).collect::<io::Result<_>>()?;
   for raw in rows{ids_out(w,&encode(&raw))?;}
  },
  9=>{
   let n=u32_in(r)?;if n>4096{return Err(io::Error::other("lookup batch bound"));}
   let rows:Vec<String>=(0..n).map(|_|text_in(r)).collect::<io::Result<_>>()?;
   for key in rows{u32_out(w,codec.find(&key)?.unwrap_or(u32::MAX))?;}
  },
  10=>{
   let ids=ids_in(r)?;
   for id in ids{let b=codec.surface(id)?;u32_out(w,b.is_some()as u32)?;if let Some(b)=b{bytes_out(w,&b)?;}}
  },
  11=>{
   let ids=ids_in(r)?;let b=codec.decode(&ids)?;u32_out(w,b.is_some()as u32)?;if let Some(b)=b{bytes_out(w,&b)?;}
  },
  12=>{
   let n=u32_in(r)?;if n>4096{return Err(io::Error::other("encodable batch bound"));}
   let rows:Vec<Vec<Part>>=(0..n).map(|_|parts_in(r)).collect::<io::Result<_>>()?;
   for parts in rows{u32_out(w,codec.encodable(&parts)?as u32)?;}
  },
  13=>{
   let parts=parts_in(r)?;let raw=bytes_in(r)?;
   match codec.encode_path(&parts,&raw)?{Ok(ids)=>{u32_out(w,0)?;ids_out(w,&ids)?;},Err(e)=>u32_out(w,e)?}
  },
  _=>return Err(io::Error::other("unknown codec command"))
 }w.flush()
}
