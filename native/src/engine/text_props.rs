#[path="text_props_data.rs"] mod data;
pub fn flags(c:char)->u32{
 let cp=c as u32;let at=data::RANGES.partition_point(|r|r.0<=cp);
 if at==0{return 0;}let r=data::RANGES[at-1];if cp<=r.1{r.2}else{0}
}
pub fn casefold(s:&str)->String{
 let mut out=String::new();
 for c in s.chars(){
  match data::FOLD.binary_search_by_key(&(c as u32),|r|r.0){
   Ok(k)=>for cp in data::FOLD[k].1{out.push(char::from_u32(*cp).unwrap());},
   Err(_)=>out.push(c)
  }
 }out
}
