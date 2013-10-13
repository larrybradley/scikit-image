import numpy as np
from skimage.segmentation import random_walker
from skimage.transform import resize


def make_2d_syntheticdata(lx, ly=None):
    if ly is None:
        ly = lx
    np.random.seed(1234)
    data = np.zeros((lx, ly)) + 0.1 * np.random.randn(lx, ly)
    small_l = int(lx / 5)
    data[lx / 2 - small_l:lx / 2 + small_l,
         ly / 2 - small_l:ly / 2 + small_l] = 1
    data[lx / 2 - small_l + 1:lx / 2 + small_l - 1,
         ly / 2 - small_l + 1:ly / 2 + small_l - 1] = \
                        0.1 * np.random.randn(2 * small_l - 2, 2 * small_l - 2)
    data[lx / 2 - small_l, ly / 2 - small_l / 8:ly / 2 + small_l / 8] = 0
    seeds = np.zeros_like(data)
    seeds[lx / 5, ly / 5] = 1
    seeds[lx / 2 + small_l / 4, ly / 2 - small_l / 4] = 2
    return data, seeds


def make_3d_syntheticdata(lx, ly=None, lz=None):
    if ly is None:
        ly = lx
    if lz is None:
        lz = lx
    np.random.seed(1234)
    data = np.zeros((lx, ly, lz)) + 0.1 * np.random.randn(lx, ly, lz)
    small_l = int(lx / 5)
    data[lx / 2 - small_l:lx / 2 + small_l,
         ly / 2 - small_l:ly / 2 + small_l,
         lz / 2 - small_l:lz / 2 + small_l] = 1
    data[lx / 2 - small_l + 1:lx / 2 + small_l - 1,
         ly / 2 - small_l + 1:ly / 2 + small_l - 1,
         lz / 2 - small_l + 1:lz / 2 + small_l - 1] = 0
    # make a hole
    hole_size = np.max([1, small_l / 8])
    data[lx / 2 - small_l,
         ly / 2 - hole_size:ly / 2 + hole_size,
         lz / 2 - hole_size:lz / 2 + hole_size] = 0
    seeds = np.zeros_like(data)
    seeds[lx / 5, ly / 5, lz / 5] = 1
    seeds[lx / 2 + small_l / 4, ly / 2 - small_l / 4, lz / 2 - small_l / 4] = 2
    return data, seeds


def test_2d_bf():
    lx = 70
    ly = 100
    data, labels = make_2d_syntheticdata(lx, ly)
    labels_bf = random_walker(data, labels, beta=90, mode='bf')
    assert (labels_bf[25:45, 40:60] == 2).all()
    assert data.shape == labels.shape
    full_prob_bf = random_walker(data, labels, beta=90, mode='bf',
                                 return_full_prob=True)
    assert (full_prob_bf[1, 25:45, 40:60] >=
            full_prob_bf[0, 25:45, 40:60]).all()
    assert data.shape == labels.shape
    # Now test with more than two labels
    labels[55, 80] = 3
    full_prob_bf = random_walker(data, labels, beta=90, mode='bf',
                                 return_full_prob=True)
    assert (full_prob_bf[1, 25:45, 40:60] >=
            full_prob_bf[0, 25:45, 40:60]).all()
    assert len(full_prob_bf) == 3
    assert data.shape == labels.shape


def test_2d_cg():
    lx = 70
    ly = 100
    data, labels = make_2d_syntheticdata(lx, ly)
    labels_cg = random_walker(data, labels, beta=90, mode='cg')
    assert (labels_cg[25:45, 40:60] == 2).all()
    assert data.shape == labels.shape
    full_prob = random_walker(data, labels, beta=90, mode='cg',
                              return_full_prob=True)
    assert (full_prob[1, 25:45, 40:60] >=
            full_prob[0, 25:45, 40:60]).all()
    assert data.shape == labels.shape
    return data, labels_cg


def test_2d_cg_mg():
    lx = 70
    ly = 100
    data, labels = make_2d_syntheticdata(lx, ly)
    labels_cg_mg = random_walker(data, labels, beta=90, mode='cg_mg')
    assert (labels_cg_mg[25:45, 40:60] == 2).all()
    assert data.shape == labels.shape
    full_prob = random_walker(data, labels, beta=90, mode='cg_mg',
                              return_full_prob=True)
    assert (full_prob[1, 25:45, 40:60] >=
            full_prob[0, 25:45, 40:60]).all()
    assert data.shape == labels.shape
    return data, labels_cg_mg


def test_types():
    lx = 70
    ly = 100
    data, labels = make_2d_syntheticdata(lx, ly)
    data = 255 * (data - data.min()) / (data.max() - data.min())
    data = data.astype(np.uint8)
    labels_cg_mg = random_walker(data, labels, beta=90, mode='cg_mg')
    assert (labels_cg_mg[25:45, 40:60] == 2).all()
    assert data.shape == labels.shape
    return data, labels_cg_mg


def test_reorder_labels():
    lx = 70
    ly = 100
    data, labels = make_2d_syntheticdata(lx, ly)
    labels[labels == 2] = 4
    labels_bf = random_walker(data, labels, beta=90, mode='bf')
    assert (labels_bf[25:45, 40:60] == 2).all()
    assert data.shape == labels.shape
    return data, labels_bf


def test_2d_inactive():
    lx = 70
    ly = 100
    data, labels = make_2d_syntheticdata(lx, ly)
    labels[10:20, 10:20] = -1
    labels[46:50, 33:38] = -2
    labels = random_walker(data, labels, beta=90)
    assert (labels.reshape((lx, ly))[25:45, 40:60] == 2).all()
    assert data.shape == labels.shape
    return data, labels


def test_3d():
    n = 30
    lx, ly, lz = n, n, n
    data, labels = make_3d_syntheticdata(lx, ly, lz)
    labels = random_walker(data, labels, mode='cg')
    assert (labels.reshape(data.shape)[13:17, 13:17, 13:17] == 2).all()
    assert data.shape == labels.shape
    return data, labels


def test_3d_inactive():
    n = 30
    lx, ly, lz = n, n, n
    data, labels = make_3d_syntheticdata(lx, ly, lz)
    old_labels = np.copy(labels)
    labels[5:25, 26:29, 26:29] = -1
    after_labels = np.copy(labels)
    labels = random_walker(data, labels, mode='cg')
    assert (labels.reshape(data.shape)[13:17, 13:17, 13:17] == 2).all()
    assert data.shape == labels.shape
    return data, labels, old_labels, after_labels


def test_multispectral_2d():
    lx, ly = 70, 100
    data, labels = make_2d_syntheticdata(lx, ly)
    data = data[..., np.newaxis].repeat(2, axis=-1)  # Expect identical output
    multi_labels = random_walker(data, labels, mode='cg', multichannel=True)
    assert data[..., 0].shape == labels.shape
    single_labels = random_walker(data[..., 0], labels, mode='cg')
    assert (multi_labels.reshape(labels.shape)[25:45, 40:60] == 2).all()
    assert data[..., 0].shape == labels.shape
    return data, multi_labels, single_labels, labels


def test_multispectral_3d():
    n = 30
    lx, ly, lz = n, n, n
    data, labels = make_3d_syntheticdata(lx, ly, lz)
    data = data[..., np.newaxis].repeat(2, axis=-1)  # Expect identical output
    multi_labels = random_walker(data, labels, mode='cg', multichannel=True)
    assert data[..., 0].shape == labels.shape
    single_labels = random_walker(data[..., 0], labels, mode='cg')
    assert (multi_labels.reshape(labels.shape)[13:17, 13:17, 13:17] == 2).all()
    assert (single_labels.reshape(labels.shape)[13:17, 13:17, 13:17] == 2).all()
    assert data[..., 0].shape == labels.shape
    return data, multi_labels, single_labels, labels


def test_depth():
    n = 30
    lx, ly, lz = n, n, n
    data, _ = make_3d_syntheticdata(lx, ly, lz)

    # Rescale `data` along Z axis
    data_aniso = np.zeros((n, n, n // 2))
    for i, yz in enumerate(data):
        data_aniso[i, :, :] = resize(yz, (n, n // 2))

    # Generate new labels
    small_l = int(lx // 5)
    labels_aniso = np.zeros_like(data_aniso)
    labels_aniso[lx // 5, ly // 5, lz // 5] = 1
    labels_aniso[lx // 2 + small_l // 4,
                 ly // 2 - small_l // 4,
                 lz // 4 - small_l // 8] = 2

    # Test with `depth` kwarg
    labels_aniso = random_walker(data_aniso, labels_aniso, mode='cg',
                                 depth=0.5)

    assert (labels_aniso[13:17, 13:17, 7:9] == 2).all()


def test_spacing():
    n = 30
    lx, ly, lz = n, n, n
    data, _ = make_3d_syntheticdata(lx, ly, lz)

    # Rescale `data` along Y axis
    # `resize` is not yet 3D capable, so this must be done by looping in 2D.
    data_aniso = np.zeros((n, n * 2, n))
    for i, yz in enumerate(data):
        data_aniso[i, :, :] = resize(yz, (n * 2, n))

    # Generate new labels
    small_l = int(lx // 5)
    labels_aniso = np.zeros_like(data_aniso)
    labels_aniso[lx // 5, ly // 5, lz // 5] = 1
    labels_aniso[lx // 2 + small_l // 4,
                 ly - small_l // 2,
                 lz // 2 - small_l // 4] = 2

    # Test with `spacing` kwarg
    # First, anisotropic along Y
    labels_aniso = random_walker(data_aniso, labels_aniso, mode='cg',
                                 spacing=(1., 2., 1.))
    assert (labels_aniso[13:17, 26:34, 13:17] == 2).all()

    # Rescale `data` along X axis
    # `resize` is not yet 3D capable, so this must be done by looping in 2D.
    data_aniso = np.zeros((n, n * 2, n))
    for i in range(data.shape[1]):
        data_aniso[i, :, :] = resize(data[:, 1, :], (n * 1.5, n))

    # Generate new labels
    small_l = int(lx // 5)
    labels_aniso = np.zeros_like(data_aniso)
    labels_aniso[lx // 5, ly // 5, lz // 5] = 1
    labels_aniso[lx - small_l // 2,
                 ly // 2 + small_l // 4,
                 lz // 2 - small_l // 4] = 2

    # Anisotropic along X
    labels_aniso2 = random_walker(np.rollaxis(data_aniso, 1).copy(),
                                  np.rollaxis(labels_aniso, 1).copy(),
                                  mode='cg', spacing=(2., 1., 1.))
    assert (labels_aniso2[26:34, 13:17, 13:17] == 2).all()


if __name__ == '__main__':
    from numpy import testing
    testing.run_module_suite()
