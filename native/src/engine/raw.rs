use std::io::{self,Read,Write};
use crate::wire::*;
use crate::raw_props::flags;
const TICK:char='\u{60}';
pub const KINDS:[&str;13]=["LAYOUT","WORD","ABBREVIATION","IDENTIFIER","HYPHENATED","PUNCTUATION","URL","EMAIL","NUMBER","ORDINAL","CODE_FENCE","INLINE_CODE","LONG_RUN"];
#[derive(Clone,Copy,Debug)]
pub struct Span{pub start:u32,pub end:u32,pub kind:u32}
impl Span{fn new(start:usize,end:usize,kind:u32)->Self{Self{start:start as u32,end:end as u32,kind}}}
pub struct Unit{pub span:Span,pub group:u32,pub index:u32}
pub struct Plan{pub chars:Vec<char>,pub units:Vec<Unit>,pub groups:Vec<Vec<Span>>,pub protected:Vec<Span>}
fn space(c:char)->bool{crate::text_props::flags(c)&4!=0}
fn bits(c:&[char],at:usize,mask:u32)->bool{c.get(at).is_some_and(|x|flags(*x)&mask!=0)}
fn starts(c:&[char],at:usize,s:&str)->bool{let mut j=at;for ch in s.chars(){if c.get(j)!=Some(&ch){return false;}j+=1;}true}
fn next_line(c:&[char],at:usize)->usize{c[at..].iter().position(|x|*x=='\n').map_or(c.len(),|j|at+j+1)}
fn newline_end(c:&[char],at:usize)->Option<usize>{
 if at==c.len(){Some(at)}else if c[at]=='\n'{Some(at+1)}
 else if c[at]=='\r' && c.get(at+1)==Some(&'\n'){Some(at+2)}else{None}
}
fn fence_at(c:&[char],line:usize,closing:Option<(char,usize)>)->Option<(usize,char,usize)>{
 if line>=c.len() || (line>0 && c[line-1]!='\n'){return None;}
 let mut j=line;while j<c.len() && j-line<3 && matches!(c[j],' '|'\t'){j+=1;}
 let ch=*c.get(j)?;let min=if let Some((expected,n))=closing{if ch!=expected{return None;}n}else{if ch!=TICK && ch!='~'{return None;}3};
 let begin=j;while j<c.len() && c[j]==ch{j+=1;}let width=j-begin;if width<min{return None;}
 if closing.is_some(){while j<c.len() && matches!(c[j],' '|'\t'){j+=1;}}
 else{while j<c.len() && !matches!(c[j],'\r'|'\n'){j+=1;}}
 newline_end(c,j).map(|end|(end,ch,width))
}
fn fence_search(c:&[char],from:usize,closing:Option<(char,usize)>)->Option<(usize,usize,char,usize)>{
 let mut line=from;
 while line<c.len(){
  if let Some((end,ch,width))=fence_at(c,line,closing){return Some((line,end,ch,width));}
  line=next_line(c,line);
 }None
}
pub fn protected(c:&[char])->Vec<Span>{
 let n=c.len();let mut found=Vec::new();let mut cursor=0;
 while let Some((start,end,ch,width))=fence_search(c,cursor,None){
  let stop=fence_search(c,end,Some((ch,width))).map_or(n,|(_,end,_,_)|end);
  found.push(Span::new(start,stop,10));cursor=stop;
 }
 // Leftmost search may begin inside a longer opening tick run when the closing run is shorter.
 let mut i=0;
 while i<n{
  if c[i]!=TICK{i+=1;continue;}let mut j=i;while j<n && c[j]==TICK{j+=1;}
  let mut k=j;while k<n && c[k]!=TICK && !matches!(c[k],'\r'|'\n'){k+=1;}
  if k==j || k==n || c[k]!=TICK{i=k;continue;}
  let mut close=k;while close<n && c[close]==TICK{close+=1;}
  let width=(j-i).min(close-k);found.push(Span::new(j-width,k+width,11));i=k+width;
 }
 i=0;
 while i<n{
  if !starts(c,i,"http"){i+=1;continue;}let mut j=i+4;if c.get(j)==Some(&'s'){j+=1;}
  if !starts(c,j,"://"){i+=1;continue;}j+=3;let body=j;
  while j<n && !space(c[j]) && !matches!(c[j],'<'|'>'){j+=1;}
  if j==body{i+=1;}else{found.push(Span::new(i,j,6));i=j;}
 }
 i=0;
 while i<n{
  if space(c[i]){i+=1;continue;}let start=i;while i<n && !space(c[i]){i+=1;}
  if i-start>=129{found.push(Span::new(start,i,12));}
 }
 found.sort_by(|a,b|(a.start,a.end,KINDS[a.kind as usize]).cmp(&(b.start,b.end,KINDS[b.kind as usize])));
 let mut merged:Vec<Span>=Vec::new();
 for s in found{
  if let Some(last)=merged.last_mut(){if s.start<last.end{last.end=last.end.max(s.end);continue;}}
  merged.push(s);
 }merged
}
fn url(c:&[char],i:usize)->Option<usize>{
 let mut j;
 if bits(c,i,64)&&bits(c,i+1,128)&&bits(c,i+2,128)&&bits(c,i+3,256){
  j=i+4;if bits(c,j,512){j+=1;}if !starts(c,j,"://"){return None;}j+=3;
 }else if bits(c,i,1024)&&bits(c,i+1,1024)&&bits(c,i+2,1024)&&c.get(i+3)==Some(&'.'){j=i+4;}
 else{return None;}
 let body=j;while j<c.len()&&!space(c[j])&&!matches!(c[j],'<'|'>'|'"'|'“'|'”'){j+=1;}
 if j==body{return None;}
 while j>i && matches!(c[j-1],'.'|','|';'|':'|'!'|'?'){j-=1;}
 for (left,right) in [('(',')'),('[',']'),('{','}') ]{
  while j>i && c[j-1]==right && c[i..j].iter().filter(|x|**x==right).count()>c[i..j].iter().filter(|x|**x==left).count(){j-=1;}
 }Some(j)
}
fn domain(c:char)->bool{flags(c)&2!=0||c=='-'}
fn email(c:&[char],i:usize)->Option<usize>{
 let mut j=i;while j<c.len()&&(flags(c[j])&2!=0||matches!(c[j],'.'|'+'|'-')){j+=1;}
 if j==i||c.get(j)!=Some(&'@'){return None;}j+=1;let start=j;while j<c.len()&&domain(c[j]){j+=1;}
 if j==start{return None;}let mut groups=0;
 while c.get(j)==Some(&'.')&&c.get(j+1).is_some_and(|x|domain(*x)){
  groups+=1;j+=2;while j<c.len()&&domain(c[j]){j+=1;}
 }if groups==0{None}else{Some(j)}
}
fn suffix_character(c:char)->bool{flags(c)&2!=0&&flags(c)&4==0&&c!='_'}
fn quoted_suffix(c:&[char],at:usize)->usize{
 let mut j=at;
 if c.get(j).is_some_and(|x|matches!(*x,'\''|'’'))&&c.get(j+1).is_some_and(|x|suffix_character(*x)){
  j+=2;while j<c.len()&&suffix_character(c[j]){j+=1;}
 }j
}
fn initial(c:char)->bool{c.is_ascii_uppercase()||matches!(c,'Ç'|'Ğ'|'İ'|'Ö'|'Ş'|'Ü')}
fn initials(c:&[char],i:usize)->Option<usize>{
 let mut j=i;let mut count=0;
 while c.get(j).is_some_and(|x|initial(*x))&&c.get(j+1)==Some(&'.'){j+=2;count+=1;}
 if count>=2{Some(quoted_suffix(c,j))}else{None}
}
fn number(c:&[char],i:usize)->Option<usize>{
 let mut j=i;if c.get(j)==Some(&'%'){j+=1;}let start=j;while bits(c,j,4){j+=1;}
 if start==j{return None;}
 while c.get(j).is_some_and(|x|matches!(*x,'.'|','|':'|'/'))&&bits(c,j+1,4){j+=2;while bits(c,j,4){j+=1;}}
 Some(quoted_suffix(c,j))
}
pub fn segment(c:&[char],abbreviations:&[String])->Vec<Span>{
 let mut spans=Vec::new();let mut i=0;let n=c.len();
 while i<n{
  if space(c[i]){i+=1;continue;}let start=i;
  if let Some(end)=url(c,i){spans.push(Span::new(i,end,6));i=end;continue;}
  let matched=if let Some(end)=email(c,i){Some((end,7))}else if let Some(end)=initials(c,i){Some((end,2))}
   else if let Some(end)=number(c,i){if bits(c,end,1){None}else{Some((end,8))}}else{None};
  if let Some((mut end,mut kind))=matched{
   if kind==8&&c[i..end].iter().all(|x|flags(*x)&8!=0)&&c.get(end)==Some(&'.'){
    let mut next=end+1;while next<n&&space(c[next]){next+=1;}
    if bits(c,next,16){end+=1;kind=9;}
   }
   spans.push(Span::new(i,end,kind));i=end;continue;
  }
  if bits(c,i,1){
   i+=1;
   while i<n{
    if bits(c,i,1){i+=1;}
    else if matches!(c[i],'\''|'’')&&bits(c,i+1,1){i+=1;}
    else if matches!(c[i],'-'|'‐'|'‑')&&bits(c,start,32)&&bits(c,i+1,32){i+=1;}
    else{break;}
   }
   let mut kind=if c[start..i].contains(&'_'){3}else if c[start..i].iter().any(|x|matches!(*x,'-'|'‐'|'‑')){4}else{1};
   if c.get(i)==Some(&'.')&&!abbreviations.is_empty(){
    let raw:String=c[start..i].iter().collect();if abbreviations.contains(&raw){i+=1;kind=2;}
   }
   spans.push(Span::new(start,i,kind));
  }else{i+=1;spans.push(Span::new(start,i,5));}
 }spans
}
fn region(c:&[char],lo:usize,hi:usize,units:&mut Vec<Unit>,groups:&mut Vec<Vec<Span>>){
 let mut lexical=segment(&c[lo..hi],&[]);let group=groups.len()as u32;let mut cursor=lo as u32;
 for (index,s) in lexical.iter_mut().enumerate(){
  s.start+=lo as u32;s.end+=lo as u32;
  if cursor<s.start{units.push(Unit{span:Span{start:cursor,end:s.start,kind:0},group:u32::MAX,index:u32::MAX});}
  units.push(Unit{span:*s,group,index:index as u32});cursor=s.end;
 }
 if cursor<hi as u32{units.push(Unit{span:Span{start:cursor,end:hi as u32,kind:0},group:u32::MAX,index:u32::MAX});}
 groups.push(lexical);
}
pub fn prepare(text:&str)->io::Result<Plan>{
 let chars:Vec<char>=text.chars().collect();let protected=protected(&chars);let mut units=Vec::new();let mut groups=Vec::new();let mut cursor=0;
 for s in &protected{
  if cursor<s.start as usize{region(&chars,cursor,s.start as usize,&mut units,&mut groups);}
  units.push(Unit{span:*s,group:u32::MAX,index:u32::MAX});cursor=s.end as usize;
 }
 if cursor<chars.len(){region(&chars,cursor,chars.len(),&mut units,&mut groups);}
 let mut cursor=0;
 for u in &units{if u.span.start!=cursor||u.span.end<=u.span.start{return Err(io::Error::other("plan coverage"));}cursor=u.span.end;}
 if cursor as usize!=chars.len(){return Err(io::Error::other("plan length"));}
 Ok(Plan{chars,units,groups,protected})
}
fn spans_out<W:Write>(w:&mut W,spans:&[Span])->io::Result<()>{
 u32_out(w,spans.len()as u32)?;for s in spans{u32_out(w,s.start)?;u32_out(w,s.end)?;u32_out(w,s.kind)?;}Ok(())
}

fn boundary_out<W:Write>(w:&mut W,p:&Plan)->io::Result<()>{
 let c=&p.chars;let units=&p.units;let mut pos=0;let mut cursor=0;let mut written=0;
 let expected=units.iter().filter(|u|matches!(u.span.kind,1|2)).count();u32_out(w,expected as u32)?;
 while pos<c.len(){
  if space(c[pos]){pos+=1;continue;}let lo=pos;while pos<c.len()&&!space(c[pos]){pos+=1;}let hi=pos;
  while cursor<units.len()&&units[cursor].span.end as usize<=lo{cursor+=1;}
  let mut last=cursor;let mut members=0;
  while last<units.len()&&(units[last].span.start as usize)<hi{if matches!(units[last].span.kind,1|2){members+=1;}last+=1;}
  for (j,u) in units.iter().enumerate().take(last).skip(cursor){
   if !matches!(u.span.kind,1|2){continue;}let start=u.span.start as usize;let end=u.span.end as usize;
   // P19 morph units contain no whitespace and belong to exactly one cluster.
   if start<lo||end>hi{return Err(io::Error::other("P19 morph cluster contract"));}
   let alnum=c[lo..start].iter().chain(&c[end..hi]).any(|ch|crate::text_props::flags(*ch)&2!=0||*ch=='_');
   let mut reason=0;
   if members!=1||alnum{reason=1;}
   else if u.span.kind==2{reason=2;}
   else if c.get(end)==Some(&'.'){
    let raw:String=c[start..end].iter().collect();
    if ["prof","dr","hz","bkz","km","vb","vs","gr","yy"].contains(&crate::text_props::casefold(&raw).as_str())
     ||(end-start==1&&crate::text_props::flags(c[start])&1!=0){reason=2;}
   }
   for v in [j,reason,lo,hi,members]{u32_out(w,v as u32)?;}written+=1;
  }
 }
 if written!=expected{return Err(io::Error::other("boundary count"));}
 Ok(())
}

fn plan_out<W:Write>(w:&mut W,_text:&str,p:Plan)->io::Result<()>{
 spans_out(w,&p.protected)?;u32_out(w,p.units.len()as u32)?;
 for u in &p.units{for v in [u.span.start,u.span.end,u.span.kind,u.group,u.index]{u32_out(w,v)?;}}
 u32_out(w,p.groups.len()as u32)?;
 for group in &p.groups{
  u32_out(w,group.len()as u32)?;
  for s in group{let word:String=p.chars[s.start as usize..s.end as usize].iter().collect();text_out(w,&word)?;}
 }
 boundary_out(w,&p)?;
 Ok(())
}
pub fn command<R:Read,W:Write>(cmd:u32,r:&mut R,w:&mut W)->io::Result<()>{
 if cmd==19{
  let n=u32_in(r)?;if n>4096{return Err(io::Error::other("property batch bound"));}
  let cps:Vec<u32>=(0..n).map(|_|u32_in(r)).collect::<io::Result<_>>()?;
  for cp in cps{let c=char::from_u32(cp).ok_or_else(||io::Error::other("invalid scalar"))?;u32_out(w,flags(c))?;}
 }else{
  let n=u32_in(r)?;if n>1024{return Err(io::Error::other("raw text batch bound"));}
  let rows:Vec<String>=(0..n).map(|_|text_in(r)).collect::<io::Result<_>>()?;
  let mut abbreviations=Vec::new();
  if cmd==17{let n=u32_in(r)?;if n>10000{return Err(io::Error::other("abbreviation count bound"));}for _ in 0..n{abbreviations.push(text_in(r)?);}}
  for text in rows{
   match cmd{
    16=>plan_out(w,&text,prepare(&text)?)?,
    17=>spans_out(w,&segment(&text.chars().collect::<Vec<_>>(),&abbreviations))?,
    18=>spans_out(w,&protected(&text.chars().collect::<Vec<_>>()))?,
    _=>return Err(io::Error::other("unknown raw command"))
   }
  }
 }w.flush()
}
