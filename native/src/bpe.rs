use std::{fs::File,io::{self,Read},path::Path,collections::BinaryHeap,cmp::Reverse};
fn bad(s:&str)->io::Error{io::Error::new(io::ErrorKind::InvalidData,s)}
fn u32in(r:&mut impl Read)->io::Result<u32>{let mut b=[0;4];r.read_exact(&mut b)?;Ok(u32::from_le_bytes(b))}
pub struct Bpe{pub pieces:Vec<Vec<u8>>,bytes:[u32;256],merges:Vec<(u32,u32,u32,u32)>,props:Vec<Vec<(u32,u32)>>}
impl Bpe{
 pub fn open(path:&Path)->io::Result<Self>{
 let mut f=File::open(path)?;let mut magic=[0;8];f.read_exact(&mut magic)?;if &magic!=b"P84BPE1\0"{return Err(bad("BPE header"))}
 let n=u32in(&mut f)?;if n!=26930{return Err(bad("BPE vocabulary"))}
 let mut pieces=Vec::new();for _ in 0..n{let n=u32in(&mut f)? as usize;if n>1000000{return Err(bad("piece length"))}let mut b=vec![0;n];f.read_exact(&mut b)?;pieces.push(b)}
 let mut bytes=[0;256];for x in &mut bytes{*x=u32in(&mut f)?}
 let n=u32in(&mut f)?;if n!=26674{return Err(bad("merge count"))}
 let mut merges=Vec::new();for _ in 0..n{merges.push((u32in(&mut f)?,u32in(&mut f)?,u32in(&mut f)?,u32in(&mut f)?))}
 merges.sort_unstable_by_key(|x|(x.0,x.1));
 let mut props=Vec::new();for _ in 0..3{let n=u32in(&mut f)?;if n>10000{return Err(bad("range count"))}let mut rr=Vec::new();for _ in 0..n{rr.push((u32in(&mut f)?,u32in(&mut f)?))}props.push(rr)}
 let mut rest=Vec::new();f.read_to_end(&mut rest)?;if !rest.is_empty(){return Err(bad("BPE trailing bytes"))}
 Ok(Self{pieces,bytes,merges,props})
 }
 fn has(&self,p:usize,c:char)->bool{let n=c as u32;let r=&self.props[p];let k=r.partition_point(|x|x.1<=n);r.get(k).is_some_and(|x|x.0<=n)}
 fn cat(&self,c:char)->u8{if self.has(0,c){1}else if self.has(1,c){2}else if self.has(2,c){4}else{3}}
 pub fn spans(&self,text:&str)->Vec<(usize,usize)>{
 let mut chars:Vec<(usize,char)>=text.char_indices().collect();chars.push((text.len(),'\0'));let n=chars.len()-1;let(mut i,mut out)=(0,Vec::new());
 while i<n{
 let lo=i;let mut contraction=0;
 if chars[i].1=='\''{for p in ["'s","'t","'re","'ve","'m","'ll","'d"]{if text[chars[i].0..].starts_with(p){contraction=p.len();break}}}
 if contraction>0{i+=contraction;}else{
 let j=if chars[i].1==' '&&i+1<n{i+1}else{i};let cat=self.cat(chars[j].1);
 if cat!=4{i=j+1;while i<n&&self.cat(chars[i].1)==cat{i+=1}}
 else{i+=1;while i<n&&self.has(2,chars[i].1){i+=1}if i<n&&i-lo>1{i-=1}}
 }
 out.push((chars[lo].0,chars[i].0));
 }out
 }
 fn push(&self,i:usize,ids:&[u32],next:&[usize],live:&[bool],heap:&mut BinaryHeap<Reverse<(u32,usize,usize,u32,u32,u32)>>){
 if i>=ids.len()||!live[i]{return}let j=next[i];if j>=ids.len(){return}
 if let Ok(k)=self.merges.binary_search_by_key(&(ids[i],ids[j]),|m|(m.0,m.1)){let(a,b,r,z)=self.merges[k];heap.push(Reverse((r,i,j,a,b,z)))}
 }
 pub fn encode(&self,text:&str)->Vec<u32>{
 let mut out=Vec::new();
 for(lo,hi)in self.spans(text){
 let mut ids:Vec<u32>=text.as_bytes()[lo..hi].iter().map(|b|self.bytes[*b as usize]).collect();let n=ids.len();
 let mut prev:Vec<usize>=(0..n).map(|i|i.wrapping_sub(1)).collect();let mut next:Vec<usize>=(1..=n).collect();let mut live=vec![true;n];let mut heap=BinaryHeap::new();
 for i in 0..n{self.push(i,&ids,&next,&live,&mut heap)}
 while let Some(Reverse((_,i,j,a,b,z)))=heap.pop(){if !live[i]||!live[j]||next[i]!=j||ids[i]!=a||ids[j]!=b{continue}
 ids[i]=z;live[j]=false;next[i]=next[j];if next[j]<n{prev[next[j]]=i}
 self.push(prev[i],&ids,&next,&live,&mut heap);self.push(i,&ids,&next,&live,&mut heap);
 }
 out.extend((0..n).filter(|i|live[*i]).map(|i|ids[i]));
 }out
 }
 pub fn decode(&self,ids:&[u32])->io::Result<Vec<u8>>{let mut b=Vec::new();for &id in ids{b.extend(self.pieces.get(id as usize).ok_or_else(||bad("BPE ID range"))?)}Ok(b)}
}
