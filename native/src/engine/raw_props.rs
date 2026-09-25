#[path="raw_props_data.rs"] mod data;
pub fn flags(c:char)->u32{
 let cp=c as u32;let at=data::RANGES.partition_point(|r|r.0<=cp);
 if at==0{return 0;}let r=data::RANGES[at-1];if cp<=r.1{r.2}else{0}
}
