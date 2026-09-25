//! Disk-backed frozen tables with a small, fixed cache of upper search nodes.
//! Values stay on disk; this does not load the full lexicon or vocabulary into RAM.
use crate::paged_file::PagedFile;
use std::io::{self,Read,Seek,SeekFrom};
use std::path::Path;
use crate::wire::*;
struct Probe {key:String,payload:u64}
pub struct Table {file:PagedFile,count:u64,length:u64,upper:Vec<Option<Probe>>}
impl Table {
    pub fn open(path:&Path)->io::Result<Self>{
        let mut file=PagedFile::open(path)?;let length=file.len();
        let mut magic=[0;8];file.read_exact(&mut magic)?;
        if &magic!=b"P73TAB1\0"{return Err(io::Error::other("table magic"));}
        let count=u64_in(&mut file)?;
        if 16+count*8>length{return Err(io::Error::other("index length"));}
        Ok(Self{file,count,length,upper:(0..127).map(|_|None).collect()})
    }
    pub fn get(&mut self,key:&str)->io::Result<Option<Vec<u8>>>{
        let(mut left,mut right,mut slot)=(0,self.count,0usize);
        while left<right{
            let at=(left+right)/2;
            let (order,payload)=if let Some(probe)=self.upper.get(slot).and_then(Option::as_ref){
                (probe.key.as_str().cmp(key),probe.payload)
            }else{
                self.file.seek(SeekFrom::Start(16+at*8))?;let offset=u64_in(&mut self.file)?;
                if offset<16+self.count*8||offset>=self.length{return Err(io::Error::other("record offset"));}
                self.file.seek(SeekFrom::Start(offset))?;let found=text_in(&mut self.file)?;
                let payload=offset+4+found.len() as u64;let order=found.as_str().cmp(key);
                if slot<self.upper.len(){self.upper[slot]=Some(Probe{key:found,payload});}
                (order,payload)
            };
            match order {
                std::cmp::Ordering::Less=>{left=at+1;slot=slot.saturating_mul(2).saturating_add(2);},
                std::cmp::Ordering::Greater=>{right=at;slot=slot.saturating_mul(2).saturating_add(1);},
                std::cmp::Ordering::Equal=>{self.file.seek(SeekFrom::Start(payload))?;return Ok(Some(bytes_in(&mut self.file)?));}
            }
        }
        Ok(None)
    }
}
pub struct Frequencies {pub words:Table,pub paths:Table}
impl Frequencies {
    pub fn word(&mut self,raw:&str)->io::Result<Vec<(String,u64)>>{
        let Some(bytes)=self.words.get(raw)?else{return Ok(Vec::new());};
        let mut reader=std::io::Cursor::new(bytes);let count=u32_in(&mut reader)?;let mut rows=Vec::new();
        for _ in 0..count{rows.push((text_in(&mut reader)?,u64_in(&mut reader)?));}Ok(rows)
    }
    pub fn path(&mut self,key:&str)->io::Result<u64>{match self.paths.get(key)?{None=>Ok(0),Some(bytes)=>u64_in(&mut std::io::Cursor::new(bytes))}}
}
