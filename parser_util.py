import configargparse


def get_parser():
    parser = configargparse.ArgumentParser()
    parser.add_argument('--config', is_config_file=True,
                        help='config file path')
    parser.add_argument("--expname", type=str, help='experiment name')
    parser.add_argument("--basedir", type=str, default='./logs/',
                        help='where to store ckpts and logs')
    parser.add_argument("--datadir", type=str,
                        default='./data/scannet/scene0050_00', help='input data directory')

    # training options
    parser.add_argument("--netdepth", type=int, default=8,
                        help='layers in network')
    parser.add_argument("--netwidth", type=int, default=256,
                        help='channels per layer')
    parser.add_argument("--netdepth_fine", type=int,
                        default=8, help='layers in fine network')
    parser.add_argument("--netwidth_fine", type=int, default=256,
                        help='channels per layer in fine network')
    parser.add_argument("--N_rand", type=int, default=32 * 32 * 4,
                        help='batch size (number of random rays per gradient step)') # разное (нужно подбирать под данные, в коде есть дефолтное значение, для разных сцен разное)
    parser.add_argument("--N_iters", type=int, default=1000000,
                        help='number of iterations for which to train the network') # = 400_000
    parser.add_argument("--lrate", type=float,
                        default=5e-4, help='learning rate') # нет в конфиге (берем дефолтный, но оптимальный может быть другой)
    parser.add_argument("--lrate_decay", type=int, default=250,
                        help='exponential learning rate decay (in 1000s)') # нет в конфиге
    parser.add_argument("--chunk", type=int, default=1024 * 32,
                        help='number of rays processed in parallel, decrease if running out of memory')
    parser.add_argument("--netchunk", type=int, default=1024 * 64,
                        help='number of pts sent through network in parallel, decrease if running out of memory')
    parser.add_argument("--no_reload", action='store_true',
                        help='do not reload weights from saved ckpt')
    parser.add_argument("--ft_path", type=str, default=None,
                        help='specific weights npy file to reload for coarse network')
    parser.add_argument("--rgb_weight", type=float,
                        default=1.0, help='weight of the img loss') # = 0.1, пока что берем дефолтные, но оптимальные могут быть другие для наших данных
    parser.add_argument("--depth_weight", type=float,
                        default=1.0, help='weight of the depth loss') # = 0
    parser.add_argument("--fs_weight", type=float,
                        default=1.0, help='weight of the free-space loss') # = 10
    parser.add_argument("--trunc_weight", type=float,
                        default=1.0, help='weight of the truncation loss') # = 6000
    parser.add_argument("--share_coarse_fine", action='store_true',
                        help='use the same network for both coarse and fine samples')
    parser.add_argument("--rgb_loss_type", type=str, default='l2',
                        help='which RGB loss to use - l1/l2 are currently supported')
    parser.add_argument("--sdf_loss_type", type=str, default='l2',
                        help='which SDF loss to use - l1/l2 are currently supported')
    parser.add_argument("--frame_features", type=int, default=0,
                        help='number of channels of the learnable per-frame features') # 2 в scene, остальное 0
    parser.add_argument("--optimize_poses", action='store_true',
                        help='optimize a pose refinement for the initial poses')
    parser.add_argument("--use_deformation_field", action='store_true',
                        help='use a deformation field to account for inaccuracies in intrinsic parameters') # True для scene

    # rendering options
    parser.add_argument("--N_samples", type=int, default=64,
                        help='number of coarse samples per ray') # разное 
    parser.add_argument("--N_importance", type=int, default=0,
                        help='number of additional fine samples per ray') # одиноковое = 16
    parser.add_argument("--perturb", type=float, default=1.,
                        help='set to 0. for no jitter, 1. for jitter') # нет в конфиге
    parser.add_argument("--use_viewdirs", action='store_true',
                        help='use full 5D input instead of 3D')  # одинаковое = True
    parser.add_argument("--i_embed", type=int, default=0,
                        help='set 0 for default positional encoding, -1 for none') # нет в конфиге 
    parser.add_argument("--multires", type=int, default=10,
                        help='log2 of max freq for positional encoding (3D location)') # одинаковое = 8
    parser.add_argument("--multires_views", type=int, default=4,
                        help='log2 of max freq for positional encoding (2D direction)') # нет в конфиге
    parser.add_argument("--raw_noise_std", type=float, default=0.,
                        help='std dev of noise added to regularize sigma_a output, 1e0 recommended') # одинаковое = 0
    parser.add_argument("--mode", type=str, default='density',
                        help='whether the network predicts density or SDF values') # одинаковое = sdf
    parser.add_argument("--trunc", type=float, default=0.05,
                        help='length of the truncation region in meters') # одинаковое = 0.05
    parser.add_argument("--render_factor", type=int, default=0,
                        help='downsampling factor to speed up rendering, set 4 or 8 for fast preview') # одинаковое = 1

    # dataset options
    parser.add_argument("--dataset_type", type=str, default='scannet',
                        help='options: llff / blender / deepvoxels / synthetic / scannet') # = scannet
    parser.add_argument("--trainskip", type=int, default=1,
                        help='will load 1/N images from the training set, useful for large datasets like deepvoxels') # = 1, 4
    parser.add_argument("--factor", type=int, default=1,
                        help='downsample factor for depth images') # = 1
    parser.add_argument("--sc_factor", type=float, default=1.0,
                        help='factor by which to scale the camera translation and the depth maps') # разное
    parser.add_argument("--translation", action="append", default=None, required=False, type=float,
                        help='translation vector for the camera poses') # разное
    parser.add_argument("--crop", type=int, default=0,
                        help='number of pixels by which to crop the image edges (e.g. due to undistortion artifacts') # есть только в "scene"
    parser.add_argument("--near", type=float, default=0.0, help='distance to the near plane') # = 0
    parser.add_argument("--far", type=float, default=1.0, help='distance to the far plane') # = 2
    
    # logging/saving options
    parser.add_argument("--i_print", type=int, default=100,
                        help='frequency of console printout and metric logging')
    parser.add_argument("--i_img", type=int, default=500,
                        help='frequency of tensorboard image logging')
    parser.add_argument("--i_weights", type=int, default=10000,
                        help='frequency of weight ckpt saving')
    parser.add_argument("--i_mesh", type=int, default=200000,
                        help='frequency of mesh extraction')

    return parser
