# /*!
#  *   Copyright (c) 2022, NVIDIA Corporation
#  *   All rights reserved.
#  *
#  *   Licensed under the Apache License, Version 2.0 (the "License");
#  *   you may not use this file except in compliance with the License.
#  *   You may obtain a copy of the License at
#  *
#  *       http://www.apache.org/licenses/LICENSE-2.0
#  *
#  *   Unless required by applicable law or agreed to in writing, software
#  *   distributed under the License is distributed on an "AS IS" BASIS,
#  *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  *   See the License for the specific language governing permissions and
#  *   limitations under the License.
#  *
#  * \file gpu_cache.py
#  * \brief API for managing a GPU Cache
#  */

from .. import backend as F
from .._ffi.function import _init_api


class GPUCache(object):
    """High-level wrapper for GPU embedding cache"""

    def __init__(self, num_items, num_feats, idtype=F.int64):
        assert idtype == F.int32 or idtype == F.int64
        self._cache = _CAPI_DGLGpuCacheCreate(
            num_items, num_feats, 32 if idtype == F.int32 else 64
        )
        self.idtype = idtype
        self.total_miss = 0
        self.total_queries = 0

    def query(self, keys):
        self.total_queries += keys.shape[0]
        keys = F.astype(keys, self.idtype)
        values, missing_index, missing_keys = _CAPI_DGLGpuCacheQuery(
            self._cache, F.to_dgl_nd(keys)
        )
        self.total_miss += missing_keys.shape[0]
        return (
            F.from_dgl_nd(values),
            F.from_dgl_nd(missing_index),
            F.from_dgl_nd(missing_keys),
        )

    def replace(self, keys, values):
        keys = F.astype(keys, self.idtype)
        values = F.astype(values, F.float32)
        _CAPI_DGLGpuCacheReplace(
            self._cache, F.to_dgl_nd(keys), F.to_dgl_nd(values)
        )

    @property
    def hit_rate(self):
        return 1 - self.total_miss / self.total_queries


_init_api("dgl.cuda", __name__)
