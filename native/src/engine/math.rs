// Calls the Windows C math runtime directly; verified against Python 3.11.9.
#[link(name="ucrt")]
extern "C" {#[link_name="exp"] fn c_exp(x:f64)->f64;#[link_name="log"] fn c_log(x:f64)->f64;#[link_name="log1p"] fn c_log1p(x:f64)->f64;}
pub fn exp(x:f64)->f64{unsafe{c_exp(x)}}
pub fn log(x:f64)->f64{unsafe{c_log(x)}}
pub fn log1p(x:f64)->f64{unsafe{c_log1p(x)}}
