//! Quick inspector for the cstr/cohere-transcribe-onnx-int8 model files.
//! Run with:
//!   cargo run --example inspect_cohere_onnx --features cohere -- \
//!     ~/.cache/voxtype-models/cohere-transcribe-int8

use std::env;
use std::path::PathBuf;

use ort::session::Session;
use ort::value::ValueType;

fn type_str(ty: &ValueType) -> String {
    match ty {
        ValueType::Tensor {
            ty,
            shape,
            dimension_symbols,
        } => {
            let dims: Vec<String> = shape
                .iter()
                .zip(dimension_symbols.iter())
                .map(|(d, sym)| {
                    if *d < 0 {
                        let s: &str = sym.as_ref();
                        if s.is_empty() {
                            "?".into()
                        } else {
                            format!("?:{s}")
                        }
                    } else {
                        d.to_string()
                    }
                })
                .collect();
            format!("Tensor<{ty:?}>[{}]", dims.join(", "))
        }
        other => format!("{other:?}"),
    }
}

fn dump(label: &str, path: &PathBuf) -> ort::Result<()> {
    println!("\n=== {label} ===");
    println!("file: {}", path.display());
    let session = Session::builder()?.commit_from_file(path)?;
    println!("inputs:");
    for (i, input) in session.inputs().iter().enumerate() {
        println!("  [{i}] {} : {}", input.name(), type_str(input.dtype()));
    }
    println!("outputs:");
    for (i, output) in session.outputs().iter().enumerate() {
        println!("  [{i}] {} : {}", output.name(), type_str(output.dtype()));
    }
    Ok(())
}

fn main() -> ort::Result<()> {
    let mut args = env::args().skip(1);
    let dir: PathBuf = args
        .next()
        .map(PathBuf::from)
        .expect("usage: inspect_cohere_onnx <model-dir> [encoder.onnx] [decoder.onnx]");
    let enc_name = args
        .next()
        .unwrap_or_else(|| "cohere-encoder.int8.onnx".to_string());
    let dec_name = args
        .next()
        .unwrap_or_else(|| "cohere-decoder.int8.onnx".to_string());
    if let Err(e) = dump("encoder", &dir.join(&enc_name)) {
        println!("encoder failed: {e}");
    }
    if let Err(e) = dump("decoder", &dir.join(&dec_name)) {
        println!("decoder failed: {e}");
    }
    Ok(())
}
