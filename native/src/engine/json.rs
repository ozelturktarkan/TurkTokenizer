//! Small JSON value used at the public boundary and for canonical path metadata.
//! No Python interpreter, embedded scripts, or external runtime dependencies.
use std::{collections::BTreeMap, io};
#[derive(Clone, Debug, PartialEq, Default)]
pub enum Value {
    #[default] Null,
    Bool(bool), Number(String), String(String), Array(Vec<Value>), Object(BTreeMap<String, Value>),
}
pub use Value as V;
pub fn err(message: &str) -> io::Error { io::Error::new(io::ErrorKind::InvalidData, message) }
pub fn s(text: impl Into<String>) -> V { V::String(text.into()) }
pub fn n(value: usize) -> V { V::Number(value.to_string()) }
pub fn f(value: f64) -> V { assert!(value.is_finite()); V::Number(crate::search_json::float(value)) }
pub fn strings<'a>(values: impl IntoIterator<Item=&'a str>) -> V { V::Array(values.into_iter().map(s).collect()) }
#[macro_export]
macro_rules! obj {
    ($($key:literal : $value:expr),* $(,)?) => {{
        let mut fields = std::collections::BTreeMap::new();
        $(fields.insert($key.to_string(), $value);)*
        $crate::json::V::Object(fields)
    }};
}
impl V {
    pub fn get(&self, key: &str) -> &V { if let V::Object(m)=self { m.get(key).unwrap_or(&V::Null) } else { &V::Null } }
    pub fn has(&self, key: &str) -> bool { matches!(self,V::Object(m) if m.contains_key(key)) }
    pub fn set(&mut self, key: &str, value: V) { if let V::Object(m)=self { m.insert(key.into(),value); } else { panic!("object required"); } }
    pub fn text(&self) -> &str { if let V::String(s)=self { s } else { panic!("string required: {self:?}"); } }
    pub fn string(&self) -> io::Result<&str> { if let V::String(s)=self { Ok(s) } else { Err(err("string required")) } }
    pub fn array(&self) -> &[V] { if let V::Array(xs)=self { xs } else { panic!("array required: {self:?}"); } }
    pub fn fields(&self) -> &BTreeMap<String,V> { if let V::Object(m)=self { m } else { panic!("object required"); } }
    pub fn boolean(&self) -> bool { matches!(self,V::Bool(true)) }
    pub fn truthy(&self) -> bool { match self { V::Null=>false,V::Bool(b)=>*b,V::Array(a)=>!a.is_empty(),V::Object(m)=>!m.is_empty(),V::String(s)=>!s.is_empty(),V::Number(s)=>s.parse::<f64>().unwrap()!=0.0 } }
    pub fn usize(&self) -> io::Result<usize> { match self {V::Number(s)=>s.parse().map_err(|_|err("nonnegative integer required")),_=>Err(err("integer required"))} }
    pub fn dump(&self) -> String { self.dump_with_spaces(false) }
    pub fn dump_with_spaces(&self, spaces: bool) -> String {
        let mut out=String::new();self.dump_into(&mut out,spaces);out
    }
    // Container assembly shares one output buffer. Escaping and number spelling
    // are unchanged; String capacities are still counted by the existing cache.
    fn dump_into(&self, out: &mut String, spaces: bool) {
        let comma=if spaces {", "}else{","};let colon=if spaces {": "}else{":"};
        match self {
            V::Null=>out.push_str("null"),
            V::Bool(b)=>out.push_str(if *b {"true"}else{"false"}),
            V::Number(s)=>out.push_str(s),
            V::String(s)=>out.push_str(&crate::search_json::quote(s)),
            V::Array(xs)=>{
                out.push('[');
                for (i,v) in xs.iter().enumerate(){if i>0{out.push_str(comma);}v.dump_into(out,spaces);}
                out.push(']');
            },
            V::Object(m)=>{
                out.push('{');
                for (i,(k,v)) in m.iter().enumerate(){
                    if i>0{out.push_str(comma);}out.push_str(&crate::search_json::quote(k));out.push_str(colon);v.dump_into(out,spaces);
                }
                out.push('}');
            },
        }
    }
    pub fn retained_bytes(&self) -> usize {
        std::mem::size_of::<Self>() + match self {
            V::String(s)|V::Number(s)=>s.capacity(),
            V::Array(xs)=>xs.capacity()*std::mem::size_of::<V>()+xs.iter().map(V::retained_bytes).sum::<usize>(),
            V::Object(m)=>m.iter().map(|(k,v)|k.capacity()+96+v.retained_bytes()).sum(),_=>0,
        }
    }
}
pub fn parse(text: &str) -> io::Result<V> {
    struct Parser<'a> { text: &'a str, at: usize }
    impl Parser<'_> {
        fn white(&mut self) { while self.at<self.text.len() && self.text.as_bytes()[self.at].is_ascii_whitespace() { self.at+=1; } }
        fn byte(&self) -> Option<u8> { self.text.as_bytes().get(self.at).copied() }
        fn consume(&mut self, b:u8)->io::Result<()> { self.white();if self.byte()!=Some(b){return Err(err("JSON delimiter"));}self.at+=1;Ok(()) }
        fn hex(&mut self)->io::Result<u32> {
            let end=self.at.checked_add(4).ok_or_else(||err("escape overflow"))?;
            let raw=self.text.get(self.at..end).ok_or_else(||err("JSON unicode escape"))?;
            let n=u32::from_str_radix(raw,16).map_err(|_|err("JSON unicode escape"))?;self.at=end;Ok(n)
        }
        fn string(&mut self)->io::Result<String> {
            self.consume(b'"')?;let mut out=String::new();
            loop {
                let b=self.byte().ok_or_else(||err("unterminated JSON string"))?;
                if b==b'"' {self.at+=1;return Ok(out);}
                if b==b'\\' {
                    self.at+=1;let escaped=self.byte().ok_or_else(||err("JSON escape"))?;self.at+=1;
                    match escaped {
                        b'"'=>out.push('"'),b'\\'=>out.push('\\'),b'/'=>out.push('/'),b'b'=>out.push('\u{8}'),b'f'=>out.push('\u{c}'),b'n'=>out.push('\n'),b'r'=>out.push('\r'),b't'=>out.push('\t'),
                        b'u'=>{let mut cp=self.hex()?;if (0xd800..=0xdbff).contains(&cp){
                            if self.text.get(self.at..self.at+2)!=Some("\\u"){return Err(err("missing low surrogate"));}self.at+=2;
                            let low=self.hex()?;if !(0xdc00..=0xdfff).contains(&low){return Err(err("low surrogate"));}cp=0x10000+((cp-0xd800)<<10)+(low-0xdc00);
                        }out.push(char::from_u32(cp).ok_or_else(||err("invalid Unicode scalar"))?);},
                        _=>return Err(err("invalid JSON escape")),
                    }
                } else {
                    if b<32{return Err(err("unescaped control character"));}
                    // ASCII delimiters cannot occur inside a UTF8 continuation.
                    // Copy the unchanged span once; escape handling stays above.
                    let start=self.at;let bytes=self.text.as_bytes();
                    while self.at<bytes.len() && bytes[self.at]>=32 && bytes[self.at]!=b'"' && bytes[self.at]!=b'\\' {self.at+=1;}
                    out.push_str(&self.text[start..self.at]);
                }
            }
        }
        fn value(&mut self, depth: usize)->io::Result<V> {
            if depth>128{return Err(err("JSON nesting limit"));}self.white();
            match self.byte().ok_or_else(||err("missing JSON value"))? {
                b'"'=>Ok(s(self.string()?)),
                b'['=>{self.at+=1;let mut xs=Vec::new();self.white();if self.byte()==Some(b']'){self.at+=1;return Ok(V::Array(xs));}
                    loop {xs.push(self.value(depth+1)?);self.white();if self.byte()==Some(b']'){self.at+=1;break;}self.consume(b',')?;}Ok(V::Array(xs))},
                b'{'=>{self.at+=1;let mut m=BTreeMap::new();self.white();if self.byte()==Some(b'}'){self.at+=1;return Ok(V::Object(m));}
                    loop {let key=self.string()?;self.consume(b':')?;let value=self.value(depth+1)?;if m.insert(key,value).is_some(){return Err(err("duplicate JSON key"));}self.white();if self.byte()==Some(b'}'){self.at+=1;break;}self.consume(b',')?;}Ok(V::Object(m))},
                b't' if self.text[self.at..].starts_with("true")=>{self.at+=4;Ok(V::Bool(true))},
                b'f' if self.text[self.at..].starts_with("false")=>{self.at+=5;Ok(V::Bool(false))},
                b'n' if self.text[self.at..].starts_with("null")=>{self.at+=4;Ok(V::Null)},
                b'-'|b'0'..=b'9'=>{
                    let start=self.at;if self.byte()==Some(b'-'){self.at+=1;}
                    if self.byte()==Some(b'0'){self.at+=1;}else{let before=self.at;while self.byte().is_some_and(|b|b.is_ascii_digit()){self.at+=1;}if self.at==before{return Err(err("JSON number"));}}
                    if self.byte()==Some(b'.'){self.at+=1;let before=self.at;while self.byte().is_some_and(|b|b.is_ascii_digit()){self.at+=1;}if self.at==before{return Err(err("JSON fraction"));}}
                    if matches!(self.byte(),Some(b'e'|b'E')){self.at+=1;if matches!(self.byte(),Some(b'+'|b'-')){self.at+=1;}let before=self.at;while self.byte().is_some_and(|b|b.is_ascii_digit()){self.at+=1;}if self.at==before{return Err(err("JSON exponent"));}}
                    let text=&self.text[start..self.at];if !text.parse::<f64>().map_err(|_|err("JSON number"))?.is_finite(){return Err(err("nonfinite JSON number"));}Ok(V::Number(text.into()))
                },_=>Err(err("invalid JSON value")),
            }
        }
    }
    let mut p=Parser{text,at:0};let value=p.value(0)?;p.white();if p.at!=text.len(){return Err(err("trailing JSON data"));}Ok(value)
}
