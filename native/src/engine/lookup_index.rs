//! Exact lookup accelerator. Fingerprints only filter; original full keys decide.
use crate::{paged_file::PagedFile,wire::{u64_in,bytes_in,text_in}};
use std::{io::{self,Read,Seek,SeekFrom},path::Path};
pub const MAGIC:&[u8;8]=b"P111IDX1";
pub const HEADER:u64=64;
pub fn fingerprint(key:&str)->u32{
 let mut h=14695981039346656037u64;
 for b in key.as_bytes(){h=(h^u64::from(*b)).wrapping_mul(1099511628211);}
 h^=h>>30;h=h.wrapping_mul(0xbf58476d1ce4e5b9);
 h^=h>>27;h=h.wrapping_mul(0x94d049bb133111eb);
 h^=h>>31;(h^(h>>32)) as u32
}
#[cfg(lookup_profile)]
thread_local!{static COUNTS:std::cell::Cell<[u64;6]>=const{std::cell::Cell::new([0;6])};}
#[cfg(lookup_profile)]
pub fn profile()->[u64;6]{COUNTS.with(|x|x.get())}
#[cfg(lookup_profile)]
fn tick(i:usize,n:u64){COUNTS.with(|x|{let mut v=x.get();v[i]+=n;x.set(v)});}
#[cfg(lookup_profile)]
fn depth(n:u64){COUNTS.with(|x|{let mut v=x.get();v[5]=v[5].max(n);x.set(v)});}
pub struct Lookup{source:PagedFile,index:PagedFile,slots:u64,source_length:u64,first_record:u64}
impl Lookup{
 pub fn open(path:&Path)->io::Result<Self>{
  let index=std::env::var_os("TURKTOKENIZER_LOOKUP_INDEX").ok_or_else(||io::Error::other("P111 lookup index path required"))?;
  let expected=option_env!("P111_LOOKUP_SHA256").ok_or_else(||io::Error::other("index SHA contract missing at build"))?;
  if crate::integrity::file_sha256(Path::new(&index))?!=expected{return Err(io::Error::other("lookup index SHA mismatch"));}
  Self::open_at(path,Path::new(&index))
 }
 pub fn open_at(path:&Path,index_path:&Path)->io::Result<Self>{
  let mut source=PagedFile::open(path)?;let source_length=source.len();
  let mut magic=[0;8];source.read_exact(&mut magic)?;
  if &magic!=b"P73TAB1\0"{return Err(io::Error::other("source table magic"));}
  let count=u64_in(&mut source)?;
  let first_record=count.checked_mul(8).and_then(|n|n.checked_add(16)).ok_or_else(||io::Error::other("source count overflow"))?;
  if first_record>source_length||source_length>u32::MAX as u64{return Err(io::Error::other("source offset range"));}
  let mut index=PagedFile::open(index_path)?;index.read_exact(&mut magic)?;
  if &magic!=MAGIC{return Err(io::Error::other("index magic"));}
  let length=u64_in(&mut index)?;let entries=u64_in(&mut index)?;let slots=u64_in(&mut index)?;let algorithm=u64_in(&mut index)?;
  let mut reserved=[0;24];index.read_exact(&mut reserved)?;
  let expected=slots.checked_mul(8).and_then(|n|n.checked_add(HEADER));
  if length!=source_length||entries!=count||!slots.is_power_of_two()||slots<=count||expected!=Some(index.len())||algorithm!=1||reserved!=[0;24]{
   return Err(io::Error::other("index/source contract"));
  }
  Ok(Self{source,index,slots,source_length,first_record})
 }
 pub fn get(&mut self,key:&str)->io::Result<Option<Vec<u8>>>{self.get_hashed(key,fingerprint(key))}
 fn get_hashed(&mut self,key:&str,fp:u32)->io::Result<Option<Vec<u8>>>{
  #[cfg(lookup_profile)] tick(0,1);
  let mut slot=u64::from(fp)&(self.slots-1);
  for step in 0..self.slots{
   #[cfg(lookup_profile)] {tick(1,1);depth(step+1);}
   #[cfg(not(lookup_profile))] let _=step;
   self.index.seek(SeekFrom::Start(HEADER+slot*8))?;
   let packed=u64_in(&mut self.index)?;let tag=packed as u32;let offset=packed>>32;
   if offset==0{
    #[cfg(lookup_profile)] tick(4,1);
    return Ok(None);
   }
   if tag==fp{
    #[cfg(lookup_profile)] tick(2,1);
    if offset<self.first_record||offset>=self.source_length{return Err(io::Error::other("index record offset"));}
    self.source.seek(SeekFrom::Start(offset))?;
    let found=text_in(&mut self.source)?;
    if found==key{
     let value=bytes_in(&mut self.source)?;
     #[cfg(lookup_profile)] tick(3,1);
     return Ok(Some(value));
    }
   }
   slot=(slot+1)&(self.slots-1);
  }
  Err(io::Error::other("index probe bound without empty slot"))
 }
 #[cfg(lookup_tests)]
 pub fn forced_get(&mut self,key:&str,fp:u32)->io::Result<Option<Vec<u8>>>{self.get_hashed(key,fp)}
}
