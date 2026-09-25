use crate::paged_file::PagedFile;
use std::io::{self,Read,Write,Seek,SeekFrom,Cursor};
use std::path::Path;
use std::collections::{BTreeMap,BTreeSet};
use crate::{wire::*,tables::Table};
#[derive(Clone,Debug)]
pub struct Lexeme {pub id:String,pub lemma:String,pub stem:String,pub pos:String,pub pronunciation:String,pub secondary:String,pub line:u32,pub attrs:Vec<String>}
impl Lexeme {
 pub fn read<R:Read>(r:&mut R)->io::Result<Self>{
  let id=text_in(r)?;let lemma=text_in(r)?;let stem=text_in(r)?;let pos=text_in(r)?;let pronunciation=text_in(r)?;let secondary=text_in(r)?;let line=u32_in(r)?;
  let n=u32_in(r)?;if n>1024{return Err(io::Error::other("attribute count"));}let mut attrs=Vec::new();for _ in 0..n{attrs.push(text_in(r)?);}
  Ok(Self{id,lemma,stem,pos,pronunciation,secondary,line,attrs})
 }
 pub fn write<W:Write>(&self,w:&mut W)->io::Result<()>{
  for s in [&self.id,&self.lemma,&self.stem,&self.pos,&self.pronunciation,&self.secondary]{text_out(w,s)?;}
  u32_out(w,self.line)?;u32_out(w,self.attrs.len()as u32)?;for a in &self.attrs{text_out(w,a)?;}Ok(())
 }
 fn has(&self,a:&str)->bool{self.attrs.iter().any(|s|s==a)}
}
struct CacheEntry {kind:usize,key:String,value:Option<Vec<u8>>}
pub struct Store {lexemes:PagedFile,count:u64,length:u64,maps:Vec<Table>,cache:Vec<CacheEntry>,retained:usize,peak_retained:usize,hits:u64,misses:u64,evictions:u64,oversize_skips:u64}

impl Store {
 pub fn open(dir:&Path)->io::Result<Self>{
  let mut lexemes=PagedFile::open(&dir.join("lexemes.bin"))?;let length=lexemes.len();let mut magic=[0;8];lexemes.read_exact(&mut magic)?;
  if &magic!=b"P76LEX1\0"{return Err(io::Error::other("lexeme magic"));}
  let count=u64_in(&mut lexemes)?;if count>(length.saturating_sub(16))/8{return Err(io::Error::other("lexeme index"));}
  let mut maps=Vec::new();for n in ["lex_entries","lex_by_stem","lex_seed_index","replay_lexemes","name_readings","bound_seeds"]{maps.push(Table::open(&dir.join(format!("{n}.bin")))?);}
  let cache=Vec::with_capacity(128);let retained=cache.capacity()*std::mem::size_of::<CacheEntry>();
  Ok(Self{lexemes,count,length,maps,cache,retained,peak_retained:retained,hits:0,misses:0,evictions:0,oversize_skips:0})
 }
 fn map(&mut self,kind:usize,key:&str)->io::Result<Option<Vec<u8>>>{
  if let Some(e)=self.cache.iter().find(|e|e.kind==kind && e.key==key){self.hits+=1;return Ok(e.value.clone());}
  self.misses+=1;let value=self.maps[kind].get(key)?;
  let fixed=self.cache.capacity()*std::mem::size_of::<CacheEntry>();let needed=key.len()+value.as_ref().map_or(0,Vec::len);
  if fixed+needed>65536{self.oversize_skips+=1;return Ok(value);}
  let entry=CacheEntry{kind,key:key.to_owned(),value:value.clone()};
  let charge=entry.key.capacity()+entry.value.as_ref().map_or(0,Vec::capacity);
  if fixed+charge>65536{self.oversize_skips+=1;return Ok(value);}
  while self.cache.len()>=128 || self.retained+charge>65536{
   let old=self.cache.remove(0);self.retained-=old.key.capacity()+old.value.as_ref().map_or(0,Vec::capacity);self.evictions+=1;
  }
  self.retained+=charge;self.cache.push(entry);self.peak_retained=self.peak_retained.max(self.retained);
  debug_assert!(self.retained<=65536 && self.cache.len()<=128);Ok(value)
 }
 pub fn stats<W:Write>(&self,w:&mut W)->io::Result<()>{
  for n in [self.hits,self.misses,self.cache.len()as u64,self.retained as u64,self.peak_retained as u64,self.evictions,self.oversize_skips]{w.write_all(&n.to_le_bytes())?;}Ok(())
 }
 pub fn replay_entry(&mut self,id:&str)->io::Result<Option<Lexeme>>{match self.map(3,id)?{None=>Ok(None),Some(b)=>{let mut xs=self.refs(&mut Cursor::new(b))?;if xs.len()!=1{return Err(io::Error::other("replay reference shape"));}Ok(xs.pop())}}}
 pub fn by_stem(&mut self,key:&str)->io::Result<Vec<Lexeme>>{match self.map(1,key)?{None=>Ok(Vec::new()),Some(b)=>self.refs(&mut Cursor::new(b))}}
 pub fn at(&mut self,id:u32)->io::Result<Lexeme>{
  if id as u64>=self.count{return Err(io::Error::other("lexeme reference"));}
  self.lexemes.seek(SeekFrom::Start(16+id as u64*8))?;let offset=u64_in(&mut self.lexemes)?;
  if offset<16+self.count*8||offset>=self.length{return Err(io::Error::other("lexeme offset"));}
  self.lexemes.seek(SeekFrom::Start(offset))?;let b=bytes_in(&mut self.lexemes)?;let mut r=Cursor::new(&b);let e=Lexeme::read(&mut r)?;
  if r.position()!=b.len()as u64{return Err(io::Error::other("lexeme trailing bytes"));}Ok(e)
 }
 fn refs<R:Read>(&mut self,r:&mut R)->io::Result<Vec<Lexeme>>{
  let n=u32_in(r)?;if n>1000000{return Err(io::Error::other("reference count"));}let mut out=Vec::new();for _ in 0..n{out.push(self.at(u32_in(r)?)?);}Ok(out)
 }
 fn named_kind(&mut self,id:&str)->io::Result<u32>{
  match self.map(4,id)?{None=>Ok(0),Some(b)=>u32_in(&mut Cursor::new(b))}
 }
 pub fn allowed(&mut self,e:&Lexeme,raw:&str,quote:u32)->io::Result<bool>{
  if e.pos=="PROPN" && !crate::unicode::first_upper(raw){return Ok(false);}
  if quote!=u32::MAX && e.pos!="PROPN"{return Ok(false);}
  let kind=self.named_kind(&e.id)?;
  if kind==2{return Ok(quote!=u32::MAX);}
  if kind==1 && quote!=u32::MAX{return Ok(quote as usize==e.stem.chars().count());}
  Ok(true)
 }
 pub fn seeds(&mut self,word:&str)->io::Result<(usize,Vec<Lexeme>)>{
  let mut found=BTreeMap::new();let ends:Vec<_>=word.char_indices().map(|(i,c)|i+c.len_utf8()).collect();
  for &end in &ends {
   if let Some(b)=self.map(2,&word[..end])?{
    for e in self.refs(&mut Cursor::new(b))?{found.insert(e.id.clone(),e);}
   }
  }
  let mut out:Vec<_>=found.into_values().collect();
  out.sort_by(|a,b|b.stem.chars().count().cmp(&a.stem.chars().count()).then(a.id.cmp(&b.id)));
  let ordinary=out.len();let mut bound=Vec::new();
  for end in std::iter::once(0).chain(ends) {
   if let Some(b)=self.map(5,&word[..end])?{
    let mut r=Cursor::new(b);let position=u32_in(&mut r)?;bound.push((position,self.refs(&mut r)?));
   }
  }
  bound.sort_by_key(|p|p.0);for (_,entries) in bound{out.extend(entries);}Ok((ordinary,out))
 }
 fn lookup<W:Write>(&mut self,kind:usize,key:&str,w:&mut W)->io::Result<()>{
  let Some(b)=self.map(kind,key)? else{return u32_out(w,0);};
  u32_out(w,1)?;let mut r=Cursor::new(b);
  if kind==4{let _=u32_in(&mut r)?;bytes_out(w,&bytes_in(&mut r)?)?;}
  else {if kind==5{let _=u32_in(&mut r)?;}let es=self.refs(&mut r)?;u32_out(w,es.len()as u32)?;for e in es{e.write(w)?;}}
  Ok(())
 }
}
fn vowel(c:char)->bool{"aeıioöuü".contains(c)}
pub fn variants(e:&Lexeme)->io::Result<BTreeSet<String>>{
 let s:Vec<char>=e.stem.chars().collect();if s.is_empty(){return Err(io::Error::other("empty lexeme stem"));}let mut out=BTreeSet::new();out.insert(e.stem.clone());let mut changed=s.clone();
 if e.has("LastVowelDrop")&&s.len()>2&&vowel(s[s.len()-2]){changed.remove(changed.len()-2);out.insert(changed.iter().collect());}
 let last=*changed.last().unwrap();
 if e.has("Voicing")&&"pçtkg".contains(last){
  let next=match last {'p'=>'b','ç'=>'c','t'=>'d','k'=>if changed.ends_with(&['n','k']){'g'}else{'ğ'},_=>'ğ'};
  *changed.last_mut().unwrap()=next;out.insert(changed.iter().collect());
 }
 if e.has("Doubling"){let mut v=changed.clone();v.push(*v.last().unwrap());out.insert(v.iter().collect());}
 if e.pos=="VERB"&&vowel(*s.last().unwrap()){out.insert(s[..s.len()-1].iter().collect());}
 if e.pos=="VERB"&&["de","ye"].contains(&e.stem.as_str()){out.insert(format!("{}i",s[0]));}
 if e.pos=="PRON"&&["ben","sen"].contains(&e.stem.as_str()){out.insert(format!("{}an",s[0]));}
 if e.pos=="PRON"&&["o","bu","şu"].contains(&e.stem.as_str()){out.insert(format!("{}n",e.stem));}
 if e.pos=="ADJ"&&["küçük","minik"].contains(&e.stem.as_str()){out.insert(s[..s.len()-1].iter().collect());}
 Ok(out)
}
pub fn command<R:Read,W:Write>(cmd:u32,r:&mut R,w:&mut W,store:&mut Store)->io::Result<()>{
 match cmd{
  20=>{let kind=u32_in(r)?as usize;if kind>=6{return Err(io::Error::other("lexical map"));}let n=u32_in(r)?;if n>128{return Err(io::Error::other("lookup batch"));}
   let mut keys=Vec::new();for _ in 0..n{keys.push(text_in(r)?);}for key in keys{store.lookup(kind,&key,w)?;}},
  21=>{let n=u32_in(r)?;if n>32{return Err(io::Error::other("seed batch"));}let mut queries=Vec::new();for _ in 0..n{queries.push((text_in(r)?,text_in(r)?,u32_in(r)?));}
   for (word,raw,quote) in queries{let (ordinary,es)=store.seeds(&word)?;u32_out(w,ordinary as u32)?;u32_out(w,es.len()as u32)?;for e in es{let allowed=store.allowed(&e,&raw,quote)?;e.write(w)?;u32_out(w,allowed as u32)?;}}},
  22=>{let n=u32_in(r)?;if n>128{return Err(io::Error::other("variant batch"));}let mut es=Vec::new();for _ in 0..n{es.push(Lexeme::read(r)?);}
   for e in es{let vs=variants(&e)?;u32_out(w,vs.len()as u32)?;for v in vs{text_out(w,&v)?;}}},
  23=>store.stats(w)?,
  _=>return Err(io::Error::other("lexicon command"))
 }w.flush()
}