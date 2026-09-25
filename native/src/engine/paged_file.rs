//! Read-only Windows file mapping for immutable, verified model data.
//! FILE_SHARE_READ prevents other handles from opening this file for writing
//! while the mapping lives. Read/Seek preserve the original logical cursor API.
use std::{ffi::c_void,fs::File,io::{self,Read,Seek,SeekFrom},os::windows::{fs::OpenOptionsExt,io::AsRawHandle},path::Path,ptr};
#[link(name="kernel32")]
extern "system" {
 fn CreateFileMappingW(file:*mut c_void,attributes:*const c_void,protection:u32,max_high:u32,max_low:u32,name:*const u16)->*mut c_void;
 fn MapViewOfFile(mapping:*mut c_void,access:u32,offset_high:u32,offset_low:u32,bytes:usize)->*mut c_void;
 fn UnmapViewOfFile(base:*const c_void)->i32;
 fn CloseHandle(handle:*mut c_void)->i32;
}
pub struct PagedFile { _file:File,length:u64,position:u64,mapping:*mut c_void,base:*const u8 }
// SAFETY: mapping is immutable and OS handles/views may move between threads.
// Cursor mutations require &mut self; shared readers cannot mutate the view.
unsafe impl Send for PagedFile {}
unsafe impl Sync for PagedFile {}
impl PagedFile {
 pub fn open(path:&Path)->io::Result<Self>{
  let file=File::options().read(true).share_mode(1).open(path)?;let length=file.metadata()?.len();
  if length>isize::MAX as u64{return Err(io::Error::new(io::ErrorKind::InvalidData,"mapping exceeds pointer range"))}
  if length==0{return Ok(Self{_file:file,length,position:0,mapping:ptr::null_mut(),base:ptr::null()})}
  // PAGE_READONLY=2 and FILE_MAP_READ=4. Map exactly the validated file length.
  let mapping=unsafe{CreateFileMappingW(file.as_raw_handle(),ptr::null(),2,0,0,ptr::null())};
  if mapping.is_null(){return Err(io::Error::last_os_error())}
  let base=unsafe{MapViewOfFile(mapping,4,0,0,length as usize)};
  if base.is_null(){let e=io::Error::last_os_error();unsafe{CloseHandle(mapping);}return Err(e)}
  Ok(Self{_file:file,length,position:0,mapping,base:base.cast()})
 }
 pub fn len(&self)->u64{self.length}
}
impl Drop for PagedFile {fn drop(&mut self){unsafe{if !self.base.is_null(){UnmapViewOfFile(self.base.cast());}if !self.mapping.is_null(){CloseHandle(self.mapping);}}}}
impl Read for PagedFile {
 fn read(&mut self,out:&mut [u8])->io::Result<usize>{
  if self.position>=self.length||out.is_empty(){return Ok(0)}
  let n=(self.length-self.position).min(out.len() as u64)as usize;
  // SAFETY: nonempty mapping retained by self; offset+n <= mapped length;
  // model is read-only; no references to the mapped region escape this method.
  let bytes=unsafe{std::slice::from_raw_parts(self.base.add(self.position as usize),n)};
  out[..n].copy_from_slice(bytes);self.position+=n as u64;Ok(n)
 }
}
impl Seek for PagedFile {
 fn seek(&mut self,from:SeekFrom)->io::Result<u64>{
  let n=match from{SeekFrom::Start(n)=>n,SeekFrom::Current(d)=>self.position.checked_add_signed(d).ok_or_else(||io::Error::new(io::ErrorKind::InvalidInput,"seek outside u64 range"))?,SeekFrom::End(d)=>self.length.checked_add_signed(d).ok_or_else(||io::Error::new(io::ErrorKind::InvalidInput,"seek outside u64 range"))?};self.position=n;Ok(n)
 }
}
#[cfg(test)]mod tests{
 use super::*;use std::io::Write;
 #[test]fn file_oracle_reads_and_seeks()->io::Result<()>{
  let root=std::env::var_os("P86_TEST_DIR").unwrap();let path=Path::new(&root).join(format!("mapping-{}.bin",std::process::id()));
  let bytes:Vec<u8>=(0..4096*67+13).map(|i|((i*131+i/11)%251)as u8).collect();File::options().write(true).create_new(true).open(&path)?.write_all(&bytes)?;
  let mut a=PagedFile::open(&path)?;let mut b=File::open(&path)?;let mut state=827516_u64;
  for i in 0..12000{state=state.wrapping_mul(6364136223846793005).wrapping_add(1);let pos=match i%5{0=>4093,1=>bytes.len()as u64-7,_=>state%(bytes.len()as u64+100)};let size=(state>>32)as usize%(4096*3+1);a.seek(SeekFrom::Start(pos))?;b.seek(SeekFrom::Start(pos))?;let mut x=vec![0;size];let mut y=vec![0;size];let nx=a.read(&mut x)?;let mut ny=0;while ny<size{let n=b.read(&mut y[ny..])?;if n==0{break}ny+=n;}assert_eq!(nx,ny);assert_eq!(&x[..nx],&y[..ny]);}
  a.seek(SeekFrom::End(-3))?;let mut end=Vec::new();a.read_to_end(&mut end)?;assert_eq!(end,bytes[bytes.len()-3..]);
  a.seek(SeekFrom::Start(0))?;assert!(a.seek(SeekFrom::Current(-1)).is_err());assert_eq!(a.stream_position()?,0);a.seek(SeekFrom::Start(u64::MAX))?;assert!(a.seek(SeekFrom::Current(1)).is_err());assert_eq!(a.read(&mut[0;1])?,0);assert_eq!(a.read(&mut[])?,0);
  assert!(File::options().write(true).open(&path).is_err());drop(a);drop(b);assert!(File::options().write(true).open(&path).is_ok());Ok(())
 }
 #[test]fn empty_and_missing_files()->io::Result<()>{
  let root=std::env::var_os("P86_TEST_DIR").unwrap();let p=Path::new(&root).join(format!("empty-{}.bin",std::process::id()));File::options().write(true).create_new(true).open(&p)?;let mut a=PagedFile::open(&p)?;assert_eq!(a.len(),0);assert_eq!(a.read(&mut[0;1])?,0);assert_eq!(a.seek(SeekFrom::End(0))?,0);assert!(a.seek(SeekFrom::End(-1)).is_err());assert!(PagedFile::open(&Path::new(&root).join("does-not-exist.bin")).is_err());Ok(())
 }
 #[test]fn traits(){fn check<T:Send+Sync>(){}check::<PagedFile>();}
}