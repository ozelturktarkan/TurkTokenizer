use std::io::{self,Read,Write};
use crate::wire::*;
use crate::text_props::{flags,casefold};
pub struct Unit{pub start:usize,pub end:usize,pub kind:u32}
pub struct Boundary{pub unit:usize,pub reason:u32,pub lo:usize,pub hi:usize,pub members:usize}
pub fn boundaries(text:&str,units:&[Unit])->io::Result<Vec<Boundary>>{
 let chars:Vec<char>=text.chars().collect();let n=chars.len();
 if units.iter().any(|u|u.start>u.end || u.end>n){return Err(io::Error::other("unit bounds"));}
 let mut result=std::collections::BTreeMap::new();let(mut pos,mut cursor)=(0,0);
 while pos<n{
  if flags(chars[pos])&4!=0{pos+=1;continue;}
  let lo=pos;while pos<n && flags(chars[pos])&4==0{pos+=1;}let hi=pos;
  while cursor<units.len() && units[cursor].end<=lo{cursor+=1;}
  let mut members=Vec::new();let mut k=cursor;
  while k<units.len() && units[k].start<hi{if units[k].kind==1 || units[k].kind==2{members.push(k);}k+=1;}
  for j in &members{
   let u=&units[*j];let raw:String=chars[u.start..u.end].iter().collect();
   let prefix=if lo<u.start{&chars[lo..u.start]}else{&chars[0..0]};
   let suffix=if u.end<hi{&chars[u.end..hi]}else{&chars[0..0]};
   let remainder_alnum=prefix.iter().chain(suffix).any(|c|flags(*c)&2!=0 || *c=='_');
   let abbreviation=["prof","dr","hz","bkz","km","vb","vs","gr","yy"].contains(&casefold(&raw).as_str());
   let reason=if members.len()!=1 || remainder_alnum{1}
    else if u.kind==2 || (u.end<n && chars[u.end]=='.' && (abbreviation || (u.end-u.start==1 && flags(chars[u.start])&1!=0))){2}else{0};
   result.insert(*j,Boundary{unit:*j,reason,lo,hi,members:members.len()});
  }
 }
 if result.len()!=units.iter().filter(|u|u.kind==1 || u.kind==2).count(){return Err(io::Error::other("missing morph boundary"));}
 Ok(result.into_values().collect())
}
pub fn command<R:Read,W:Write>(r:&mut R,w:&mut W)->io::Result<()>{
 let text=text_in(r)?;let n=u32_in(r)?;if n>100000{return Err(io::Error::other("unit count bound"));}
 let mut units=Vec::with_capacity(n as usize);
 for _ in 0..n{units.push(Unit{start:u32_in(r)?as usize,end:u32_in(r)?as usize,kind:u32_in(r)?});}
 let bs=boundaries(&text,&units)?;u32_out(w,bs.len()as u32)?;
 for b in bs{for v in [b.unit,b.reason as usize,b.lo,b.hi,b.members]{u32_out(w,v as u32)?;}}
 w.flush()
}
