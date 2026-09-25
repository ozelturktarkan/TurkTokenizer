use std::io;
use crate::unicode;
fn fail()->io::Error{io::Error::other("invalid canonical JSON path")}
struct Parser<'a>{b:&'a[u8],p:usize}
impl<'a> Parser<'a>{
    fn ws(&mut self){while self.p<self.b.len() && matches!(self.b[self.p],b' '|b'\n'|b'\r'|b'\t'){self.p+=1;}}
    fn expect(&mut self,c:u8)->io::Result<()>{self.ws();if self.b.get(self.p)!=Some(&c){return Err(fail());}self.p+=1;Ok(())}
    fn hex(&mut self)->io::Result<u32>{
        let mut n=0;for _ in 0..4{let c=*self.b.get(self.p).ok_or_else(fail)?;self.p+=1;n=n*16+match c{b'0'..=b'9'=>(c-b'0')as u32,b'a'..=b'f'=>(c-b'a'+10)as u32,b'A'..=b'F'=>(c-b'A'+10)as u32,_=>return Err(fail())};}Ok(n)
    }
    fn string(&mut self)->io::Result<String>{
        self.expect(b'"')?;let mut bytes=Vec::new();
        loop{let c=*self.b.get(self.p).ok_or_else(fail)?;self.p+=1;
            match c{
                b'"'=>return String::from_utf8(bytes).map_err(|_|fail()),
                b'\\'=>{let escaped=*self.b.get(self.p).ok_or_else(fail)?;self.p+=1;
                    match escaped {
                        b'"'|b'\\'|b'/'=>bytes.push(escaped),b'b'=>bytes.push(8),b'f'=>bytes.push(12),b'n'=>bytes.push(10),b'r'=>bytes.push(13),b't'=>bytes.push(9),
                        b'u'=>{let mut cp=self.hex()?;if (0xD800..=0xDBFF).contains(&cp){if self.b.get(self.p..self.p+2)!=Some(b"\\u"){return Err(fail());}self.p+=2;let low=self.hex()?;if !(0xDC00..=0xDFFF).contains(&low){return Err(fail());}cp=0x10000+((cp-0xD800)<<10)+(low-0xDC00);}
                            let c=char::from_u32(cp).ok_or_else(fail)?;let mut buf=[0;4];bytes.extend_from_slice(c.encode_utf8(&mut buf).as_bytes());},
                        _=>return Err(fail())
                    }
                },
                0..=31=>return Err(fail()),_=>bytes.push(c)
            }
        }
    }
}
pub fn path(key:&str)->io::Result<(String,String,Vec<(String,String)>,String)>{
    let mut p=Parser{b:key.as_bytes(),p:0};p.expect(b'[')?;let root=p.string()?;p.expect(b',')?;let rp=p.string()?;p.expect(b',')?;p.expect(b'[')?;
    let mut events=Vec::new();p.ws();
    if p.b.get(p.p)!=Some(&b']'){
        loop{p.expect(b'[')?;let m=p.string()?;p.expect(b',')?;let pos=p.string()?;p.expect(b']')?;events.push((m,pos));p.ws();if p.b.get(p.p)!=Some(&b','){break;}p.p+=1;}
    }
    p.expect(b']')?;p.expect(b',')?;let final_pos=p.string()?;p.expect(b']')?;p.ws();if p.p!=p.b.len(){return Err(fail());}
    Ok((root,rp,events,final_pos))
}
const fn crc_table()->[u32;256]{let mut table=[0;256];let mut n=0;while n<256{let mut c=n as u32;let mut i=0;while i<8{c=if c&1!=0{0xedb88320^(c>>1)}else{c>>1};i+=1;}table[n]=c;n+=1;}table}
const CRC:[u32;256]=crc_table();
pub fn crc32(s:&str)->u32 {let mut c=0xffffffff;for &b in s.as_bytes(){c=CRC[((c^(b as u32))&255)as usize]^(c>>8);}c^0xffffffff}
fn unique(mut values:Vec<u32>)->Vec<u32>{values.sort_unstable();values.dedup();values}
fn relevant(mid:&str)->bool{["CASE_","POSS_","AGR_"].iter().any(|p|mid.starts_with(p))}
fn signature_mid(mid:&str)->bool{relevant(mid)||mid.starts_with("PART_")||mid.starts_with("CONV_")}
fn pybool(b:bool)->&'static str{if b{"True"}else{"False"}}

fn crc_update(mut state:u32,text:&str)->u32{for &b in text.as_bytes(){state=CRC[((state^(b as u32))&255)as usize]^(state>>8);}state}
fn prefix(text:&str)->u32{crc_update(0xffffffff,text)}
fn append(mut state:u32,parts:&[&str])->u32{for text in parts{state=crc_update(state,text);}state^0xffffffff}
/// Only raw-word/context dependent work; rebuilt per rank call, never a sentence-result cache.
pub struct Prepared {word_prefix:u32,capital_prefix:u32,endings:Vec<u32>,neighbors:Vec<(u32,Option<u32>)>,bags:Vec<u32>}
pub fn prepare(words:&[String],i:usize)->io::Result<Prepared>{
 if i>=words.len(){return Err(io::Error::other("word index"));}
 let raw=&words[i];let word=unicode::lower(raw);let letters:Vec<char>=word.chars().collect();
 let mut endings=Vec::new();
 for size in [2,3,4]{if letters.len()>=size{let ending:String=letters[letters.len()-size..].iter().collect();endings.push(prefix(&format!("END{size}={ending}|")));}}
 let mut neighbors=Vec::new();
 for off in [-3,-2,-1,1,2,3]{
  let j=i as isize+off;let inbounds=j>=0&&(j as usize)<words.len();
  let neighbor=if inbounds{unicode::lower(&words[j as usize])}else if j<0{"<BOS>".to_owned()}else{"<EOS>".to_owned()};
  neighbors.push((prefix(&format!("N{off}={neighbor}|")),if inbounds{Some(prefix(&format!("NC{off}={}|",pybool(unicode::first_upper(&words[j as usize])))))}else{None}));
 }
 let mut bags=Vec::new();
 for direction in [-1isize,1]{for dist in 4..13{
  let j=i as isize+dist*direction;if j<0||j as usize>=words.len(){break;}
  let j=j as usize;if words[(i.min(j)+1)..i.max(j)].iter().any(|w|matches!(w.as_str(),"."|";"|"!"|"?")){break;}
  let neighbor=unicode::lower(&words[j]);bags.push(prefix(&format!("BAG{direction}={neighbor}|")));
 }}
 Ok(Prepared{word_prefix:prefix(&format!("W={word}|")),capital_prefix:prefix(&format!("CAP={}|",pybool(unicode::first_upper(raw)))),endings,neighbors,bags})
}

/// Per-request observations of one original raw-text group. Contains no decisions.
struct GroupWord {normalized:String,capital:bool,bag:[u32;2],punctuation:bool}
pub struct Group {words:Vec<GroupWord>}
pub fn group(words:&[String])->Group {
 Group{words:words.iter().map(|raw|{
  let normalized=unicode::lower(raw);
  let bag=[prefix(&format!("BAG-1={normalized}|")),prefix(&format!("BAG1={normalized}|"))];
  GroupWord{normalized,capital:unicode::first_upper(raw),bag,punctuation:matches!(raw.as_str(),"."|";"|"!"|"?")}
 }).collect()}
}
pub fn prepare_group_at(group:&Group,i:usize)->io::Result<Prepared>{
 let words=&group.words;
 if i>=words.len(){return Err(io::Error::other("word index"));}
 let raw=&words[i];let word=&raw.normalized;let letters:Vec<char>=word.chars().collect();
 let mut endings=Vec::new();
 for size in [2,3,4]{if letters.len()>=size{let ending:String=letters[letters.len()-size..].iter().collect();endings.push(prefix(&format!("END{size}={ending}|")));}}
 let mut neighbors=Vec::new();
 for off in [-3,-2,-1,1,2,3]{
  let j=i as isize+off;let inbounds=j>=0&&(j as usize)<words.len();
  let neighbor=if inbounds{words[j as usize].normalized.as_str()}else if j<0{"<BOS>"}else{"<EOS>"};
  neighbors.push((prefix(&format!("N{off}={neighbor}|")),if inbounds{Some(prefix(&format!("NC{off}={}|",pybool(words[j as usize].capital))))}else{None}));
 }
 let mut bags=Vec::new();
 for direction in [-1isize,1]{for dist in 4..13{
  let j=i as isize+dist*direction;if j<0||j as usize>=words.len(){break;}
  let j=j as usize;if words[(i.min(j)+1)..i.max(j)].iter().any(|w|w.punctuation){break;}
  bags.push(words[j].bag[usize::from(direction>0)]);
 }}
 Ok(Prepared{word_prefix:prefix(&format!("W={word}|")),capital_prefix:prefix(&format!("CAP={}|",pybool(raw.capital))),endings,neighbors,bags})
}

fn raw_prepared(prepared:&Prepared,parsed:&(String,String,Vec<(String,String)>,String))->(Vec<u32>,Vec<u32>){
 let(root,rp,events,final_pos)=parsed;
 let signature=format!("{}/{}",final_pos,events.iter().filter(|e|signature_mid(&e.0)).map(|e|e.0.as_str()).collect::<Vec<_>>().join("/"));
 // Hash each descriptor directly from borrowed pieces. Final sort/dedup is unchanged.
 let mut local=Vec::with_capacity(15+4*events.len()+prepared.endings.len());
 let emit=|local:&mut Vec<u32>,parts:&[&str]|{
  local.push(append(0xffffffff,parts));
  local.push(append(prepared.word_prefix,parts));
 };
 emit(&mut local,&["P=",final_pos]);
 emit(&mut local,&["RP=",rp]);
 emit(&mut local,&["RP_P=",rp,":",final_pos]);
 emit(&mut local,&["R=",root]);
 emit(&mut local,&["R_P=",root,":",final_pos]);
 emit(&mut local,&["SIG=",&signature]);
 let mut path_state=prefix("PATH=");
 let mut word_path_state=crc_update(prepared.word_prefix,"PATH=");
 for (j,(mid,pos)) in events.iter().enumerate(){
  if j>0{path_state=crc_update(path_state,";");word_path_state=crc_update(word_path_state,";");}
  for part in [mid.as_str(),":",pos.as_str()]{path_state=crc_update(path_state,part);word_path_state=crc_update(word_path_state,part);}
 }
 local.push(path_state^0xffffffff);local.push(word_path_state^0xffffffff);
 for (j,(mid,pos)) in events.iter().enumerate(){
  emit(&mut local,&["M=",mid,":",pos]);
  if j>0{emit(&mut local,&["MM=",&events[j-1].0,":",mid]);}
 }
 local.push(append(prepared.capital_prefix,&[final_pos]));
 for &state in &prepared.endings{local.push(append(state,&[&signature]));}
 // Context targets use the same bytes without allocating formatted strings.
 let mut context=Vec::new();
 for &(neighbor,capital) in &prepared.neighbors{
  context.push(append(neighbor,&["P=",final_pos]));
  context.push(append(neighbor,&["SIG=",&signature]));
  context.push(append(neighbor,&["R=",root]));
  for (mid,_) in events{context.push(append(neighbor,&["M=",mid]));}
  if let Some(capital)=capital{context.push(append(capital,&[&signature]));}
 }
 for &neighbor in &prepared.bags{
  context.push(append(neighbor,&["P=",final_pos]));
  for (mid,_) in events{if relevant(mid){context.push(append(neighbor,&["M=",mid]));}}
 }
 (local,context)
}
/// Preserve full CRC arrays for callers that request them.
pub fn extract_prepared(prepared:&Prepared,parsed:&(String,String,Vec<(String,String)>,String))->io::Result<(Vec<u32>,Vec<u32>,Vec<u32>)>{
 let(local,context)=raw_prepared(prepared,parsed);
 let local=unique(local);let context=unique(context);let mut indices=unique(local.iter().map(|x|x%524288).collect());
 indices.extend(unique(context.iter().map(|x|524288+x%524288).collect()));
 Ok((local,context,indices))
}
/// Dedup after projection preserves the set, including CRC bucket collisions.
/// Disjoint local/context ranges and their sorted order preserve f32 sum order.
pub(crate) fn project_indices(mut local:Vec<u32>,mut context:Vec<u32>)->Vec<u32>{
 for x in &mut local{*x%=524288;}
 for x in &mut context{*x=524288+*x%524288;}
 let mut indices=unique(local);indices.extend(unique(context));indices
}
pub(crate) fn indices_prepared(prepared:&Prepared,parsed:&(String,String,Vec<(String,String)>,String))->io::Result<Vec<u32>>{
 let(local,context)=raw_prepared(prepared,parsed);Ok(project_indices(local,context))
}
pub fn extract(words:&[String],i:usize,key:&str)->io::Result<(Vec<u32>,Vec<u32>,Vec<u32>)>{let prepared=prepare(words,i)?;let parsed=path(key)?;extract_prepared(&prepared,&parsed)}
