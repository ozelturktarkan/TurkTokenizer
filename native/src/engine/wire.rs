use std::io::{self,Read,Write};
pub fn u32_in<R:Read>(r:&mut R)->io::Result<u32>{let mut b=[0;4];r.read_exact(&mut b)?;Ok(u32::from_le_bytes(b))}
pub fn u64_in<R:Read>(r:&mut R)->io::Result<u64>{let mut b=[0;8];r.read_exact(&mut b)?;Ok(u64::from_le_bytes(b))}
pub fn f64_in<R:Read>(r:&mut R)->io::Result<f64>{Ok(f64::from_bits(u64_in(r)?))}
pub fn bytes_in<R:Read>(r:&mut R)->io::Result<Vec<u8>>{let n=u32_in(r)?as usize;if n>16*1024*1024{return Err(io::Error::other("prototype frame bound"));}let mut b=vec![0;n];r.read_exact(&mut b)?;Ok(b)}
pub fn text_in<R:Read>(r:&mut R)->io::Result<String>{String::from_utf8(bytes_in(r)?).map_err(|_|io::Error::other("invalid UTF8"))}
pub fn u32_out<W:Write>(w:&mut W,n:u32)->io::Result<()>{w.write_all(&n.to_le_bytes())}
pub fn f64_out<W:Write>(w:&mut W,n:f64)->io::Result<()>{w.write_all(&n.to_bits().to_le_bytes())}
pub fn bytes_out<W:Write>(w:&mut W,b:&[u8])->io::Result<()>{u32_out(w,b.len()as u32)?;w.write_all(b)}
pub fn text_out<W:Write>(w:&mut W,s:&str)->io::Result<()>{bytes_out(w,s.as_bytes())}
pub fn map_out<W:Write>(w:&mut W,fs:&[(String,f64)])->io::Result<()>{u32_out(w,fs.len()as u32)?;for(k,v)in fs{text_out(w,k)?;f64_out(w,*v)?;}Ok(())}
pub fn map_in<R:Read>(r:&mut R)->io::Result<Vec<(String,f64)>>{let n=u32_in(r)?;if n>10000{return Err(io::Error::other("feature map bound"));}let mut fs=Vec::new();for _ in 0..n{fs.push((text_in(r)?,f64_in(r)?));}Ok(fs)}
