// Exact P71 summation bodies; only sum visibility changed.
fn pairwise(values: &[f32]) -> f32 {
    let count = values.len();
    if count < 8 {
        let mut sum = -0.0_f32;
        for &value in values { sum += value; }
        return sum;
    }
    if count > 128 {
        let middle = (count / 2) & !7;
        return pairwise(&values[..middle]) + pairwise(&values[middle..]);
    }
    let mut lanes = [0.0_f32; 8];
    lanes.copy_from_slice(&values[..8]);
    let end = count & !7;
    for block in values[8..end].chunks_exact(8) {
        for lane in 0..8 { lanes[lane] += block[lane]; }
    }
    let left = (lanes[0] + lanes[1]) + (lanes[2] + lanes[3]);
    let right = (lanes[4] + lanes[5]) + (lanes[6] + lanes[7]);
    let mut result = left + right;
    for &value in &values[end..] { result += value; }
    result
}
pub fn sum(values: &[f32]) -> f32 {
    // NumPy add.reduce uses its positive-zero additive identity.
    0.0_f32 + pairwise(values)
}
