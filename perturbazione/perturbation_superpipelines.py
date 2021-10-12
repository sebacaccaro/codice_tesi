import json
from pipeline import DetokenizerModule, SuperPipeline, TokenizerModule
from pipelines_def import segmentation_pipeline, token_pipeline, token_pipeline_token_version

tokenSub_activated = True

with open("../Perturbazione/submatrix_extraction/error_matrix.json") as f:
    subData = json.load(f)

altDict = {}

easySegPipeline = segmentation_pipeline(p_mergehyphen=0.001,
                                        p_splitcomma=0.001,
                                        p_split=0.0025,
                                        p_punctadd=0.005)

mediumSegPipeline = segmentation_pipeline(p_mergehyphen=0.001,
                                          p_splitcomma=0.002,
                                          p_split=0.008,
                                          p_punctadd=0.025)

hardSegPipeline = segmentation_pipeline(p_mergehyphen=0.01,
                                        p_splitcomma=0.02,
                                        p_split=0.05,
                                        p_punctadd=0.1)

easySegPipeline.addTokenization(TokenizerModule())
mediumSegPipeline.addTokenization(TokenizerModule())
hardSegPipeline.addTokenization(TokenizerModule())

S1 = SuperPipeline(stickyness=0.8,
                   block_size=800,
                   detokenizer=DetokenizerModule())

S2 = SuperPipeline(stickyness=0.8,
                   block_size=800,
                   detokenizer=DetokenizerModule())

S3 = SuperPipeline(stickyness=0.8,
                   block_size=800,
                   detokenizer=DetokenizerModule())

S1.addPipeline(easySegPipeline, weight=6)
S1.addPipeline(mediumSegPipeline, weight=4)
S1.addPipeline(hardSegPipeline, weight=1)

S2.addPipeline(easySegPipeline, weight=2)
S2.addPipeline(mediumSegPipeline, weight=8)
S2.addPipeline(hardSegPipeline, weight=1)

S3.addPipeline(easySegPipeline, weight=1)
S3.addPipeline(mediumSegPipeline, weight=6)
S3.addPipeline(hardSegPipeline, weight=4)

easyTknPipeline = token_pipeline(p_charsub=0.1, sub_data=subData)

mediumTknPipeline = token_pipeline(p_charsub=0.3, sub_data=subData)

hardTknPipeline = token_pipeline(p_charsub=0.8, sub_data=subData)

if tokenSub_activated:
    easyTknPipeline = token_pipeline_token_version(p_tokensub=0.1,
                                                   sub_data=subData,
                                                   altDict=altDict)

    mediumTknPipeline = token_pipeline_token_version(p_tokensub=0.3,
                                                     sub_data=subData,
                                                     altDict=altDict)

    hardTknPipeline = token_pipeline_token_version(p_tokensub=0.8,
                                                   sub_data=subData,
                                                   altDict=altDict)

eTkn = easyTknPipeline.clone()
mTkn = mediumTknPipeline.clone()
hTkn = hardTknPipeline.clone()

easyTknPipeline.addTokenization(TokenizerModule())
mediumTknPipeline.addTokenization(TokenizerModule())
hardTknPipeline.addTokenization(TokenizerModule())

T1 = SuperPipeline(stickyness=0.8,
                   block_size=800,
                   detokenizer=DetokenizerModule())

T2 = SuperPipeline(stickyness=0.8,
                   block_size=800,
                   detokenizer=DetokenizerModule())

T3 = SuperPipeline(stickyness=0.8,
                   block_size=800,
                   detokenizer=DetokenizerModule())

T1.addPipeline(easyTknPipeline, weight=6)
T1.addPipeline(mediumTknPipeline, weight=4)
T1.addPipeline(hardTknPipeline, weight=1)

T2.addPipeline(easyTknPipeline, weight=2)
T2.addPipeline(mediumTknPipeline, weight=8)
T2.addPipeline(hardTknPipeline, weight=1)

T3.addPipeline(easyTknPipeline, weight=1)
T3.addPipeline(mediumTknPipeline, weight=6)
T3.addPipeline(hardTknPipeline, weight=4)

M1 = SuperPipeline(stickyness=0.8,
                   block_size=800,
                   detokenizer=DetokenizerModule())

M2 = SuperPipeline(stickyness=0.8,
                   block_size=800,
                   detokenizer=DetokenizerModule())

M3 = SuperPipeline(stickyness=0.8,
                   block_size=800,
                   detokenizer=DetokenizerModule())

easyMixedPipeline = easySegPipeline.clone().concatPipeline(eTkn)
mediumMixedPipeline = mediumSegPipeline.clone().concatPipeline(mTkn)
hardMixedPipeline = hardSegPipeline.clone().concatPipeline(hTkn)

M1.addPipeline(easyMixedPipeline, weight=6)
M1.addPipeline(mediumMixedPipeline, weight=4)
M1.addPipeline(hardMixedPipeline, weight=1)

M2.addPipeline(easyMixedPipeline, weight=2)
M2.addPipeline(mediumMixedPipeline, weight=8)
M2.addPipeline(hardMixedPipeline, weight=1)

M3.addPipeline(easyMixedPipeline, weight=1)
M3.addPipeline(mediumMixedPipeline, weight=6)
M3.addPipeline(hardMixedPipeline, weight=4)

sup_pipelines = {
    "M1": M1,
    "M2": M2,
    "M3": M3,
    "S1": S1,
    "S2": S2,
    "S3": S3,
    "T1": T1,
    "T2": T2,
    "T3": T3
}
