mod data { include!("unicode14_data.rs"); }
fn props(cp:u32)->(u8,u8) {
    let at=data::PROPERTIES.partition_point(|r|r.0<=cp);
    if at==0{return (0,0);}
    let r=data::PROPERTIES[at-1];
    if cp<=r.1{(r.2,r.3)}else{(0,0)}
}
fn mapping(table:&'static [(u32,&'static [u32])],cp:u32)->Option<&'static [u32]> {
    table.binary_search_by_key(&cp,|r|r.0).ok().map(|i|table[i].1)
}
fn decompose(cp:u32,out:&mut Vec<u32>) {
    if (0xAC00..0xD7A4).contains(&cp) {
        let s=cp-0xAC00;decompose(0x1100+s/588,out);decompose(0x1161+(s%588)/28,out);
        if s%28!=0{decompose(0x11A7+s%28,out);} return;
    }
    if let Some(seq)=mapping(data::DECOMPOSITION,cp){for &v in seq{decompose(v,out);}return;}
    out.push(cp);let ccc=props(cp).1;
    if ccc!=0 {let mut at=out.len()-1;while at>0 && props(out[at-1]).1>ccc {out.swap(at-1,at);at-=1;}}
}
fn compose(a:u32,b:u32)->Option<u32> {
    if (0x1100..0x1113).contains(&a) && (0x1161..0x1176).contains(&b){return Some(0xAC00+(a-0x1100)*588+(b-0x1161)*28);}
    if (0xAC00..0xD7A4).contains(&a) && (a-0xAC00)%28==0 && (0x11A8..0x11C3).contains(&b){return Some(a+b-0x11A7);}
    data::COMPOSITION.binary_search_by_key(&(a,b),|r|(r.0,r.1)).ok().map(|i|data::COMPOSITION[i].2)
}
pub fn nfc(raw:&str)->Vec<u32> {
    let mut decomposed=Vec::with_capacity(raw.chars().count());for c in raw.chars(){decompose(c as u32,&mut decomposed);}
    if decomposed.is_empty(){return decomposed;}
    let mut out=Vec::with_capacity(decomposed.len());out.push(decomposed[0]);
    let mut starter=0;let mut last_ccc=props(decomposed[0]).1;
    for &cp in &decomposed[1..] {
        let ccc=props(cp).1;
        if let Some(combined)=compose(out[starter],cp).filter(|_|last_ccc<ccc || last_ccc==0){out[starter]=combined;}
        else {if ccc==0{starter=out.len();}out.push(cp);last_ccc=ccc;}
    }
    out
}
pub fn lower(raw:&str)->String {
    let mut chars=nfc(raw);for cp in &mut chars{if *cp==0x49{*cp=0x131;}else if *cp==0x130{*cp=0x69;}}
    let mut out=String::with_capacity(raw.len());
    for (i,&cp) in chars.iter().enumerate() {
        if cp==0x3A3 {
            let before=chars[..i].iter().rev().find(|&&c|props(c).0&2==0).is_some_and(|&c|props(c).0&1!=0);
            let after=chars[i+1..].iter().find(|&&c|props(c).0&2==0).is_some_and(|&c|props(c).0&1!=0);
            out.push(if before && !after{'ς'}else{'σ'});
        } else if let Some(seq)=mapping(data::LOWER,cp) {for &c in seq{out.push(char::from_u32(c).unwrap());}}
        else {out.push(char::from_u32(cp).unwrap());}
    }
    out
}
pub fn first_upper(raw:&str)->bool {raw.chars().next().is_some_and(|c|props(c as u32).0&4!=0)}

pub fn all_upper(raw:&str)->bool {let mut cased=false;for c in raw.chars(){let f=props(c as u32).0;if f&1!=0{if f&4==0{return false;}cased=true;}}cased}
