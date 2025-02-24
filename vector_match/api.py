from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from core import getLSH

app = FastAPI(
    title="LSH API",
    description="テキストのLSH（Locality Sensitive Hashing）シグネチャを生成するAPI",
    version="1.0.0"
)

class TextInput(BaseModel):
    text: str
    num_perm: Optional[int] = 512
    ensemble_size: Optional[int] = 10
    use_binning: Optional[bool] = False
    round_digits_or_bin_size: Optional[float] = 0.01
    base_seed: Optional[int] = 42

class LSHResponse(BaseModel):
    text: str
    lsh_signature: str

@app.post("/lsh", response_model=LSHResponse)
async def get_lsh_signature(input_data: TextInput):
    """
    テキストからLSHシグネチャを生成します。

    - **text**: 入力テキスト
    - **num_perm**: MinHashのパーミテーション数（デフォルト: 512）
    - **ensemble_size**: アンサンブルサイズ（デフォルト: 10）
    - **use_binning**: ビニング使用フラグ（デフォルト: False）
    - **round_digits_or_bin_size**: 丸め桁数またはビンサイズ（デフォルト: 0.01）
    - **base_seed**: 基本シード値（デフォルト: 42）
    """
    try:
        lsh_result = getLSH(
            text=input_data.text,
            num_perm=input_data.num_perm,
            ensemble_size=input_data.ensemble_size,
            use_binning=input_data.use_binning,
            round_digits_or_bin_size=input_data.round_digits_or_bin_size,
            base_seed=input_data.base_seed
        )
        
        return LSHResponse(
            text=input_data.text,
            lsh_signature=lsh_result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 