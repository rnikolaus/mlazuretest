import argparse
import os
import sys

import ray
from ray.rllib import train
from ray import tune

from azureml.core import Run

from utils import callbacks
import BCTrade_utils
import distutils.dir_util


DEFAULT_RAY_ADDRESS = 'localhost:6379'


if __name__ == "__main__":
    
    
    # Parse arguments and add callbacks to config
    train_parser = train.create_parser()

    args = train_parser.parse_args()
    args.config["callbacks"] = {"on_train_result": callbacks.on_train_result}
    #args.config["render_env"] = True

    # Trace if video capturing is on
    if 'monitor' in args.config and args.config['monitor']:
        print("Video capturing is ON!")

    # Start (connect to) Ray cluster
    if args.ray_address is None:
        args.ray_address = DEFAULT_RAY_ADDRESS

    ray.init(address=args.ray_address)

    x = eval(args.env)
    
    # Get a handle to run
    run = Run.get_context()


    checkpoint=None
    if 'checkpoint' in x:

        # Get handles to the tarining artifacts dataset and mount path
        artifacts_dataset = run.input_datasets['artifacts_dataset']
        artifacts_path = run.input_datasets['artifacts_path']
        checkpoint_id=x['checkpoint']
        checkpoint_files = list(filter(
        lambda filename: filename.endswith(checkpoint_id),
            artifacts_dataset.to_path()))

        checkpoint_file = checkpoint_files[0]
        if checkpoint_file[0] == '/':
            checkpoint_file = checkpoint_file[1:]
       
        checkpoint_d,checkpoint_f = os.path.split(os.path.join(artifacts_path, checkpoint_file))
        
        destdir = os.path.join(args.local_dir,"checkpoint")
        
        distutils.dir_util.copy_tree(checkpoint_d, destdir)
        checkpoint = os.path.join(destdir,checkpoint_f)
        print('Checkpoint:', checkpoint)
        #checkpoint = os.path.join(args.local_dir,checkpoint_file)




    tune.run(
        run_or_experiment=args.run,
        config=dict(args.config, env=BCTrade_utils.registerBCTrade(x['name'],singlerun=x['singlerun'],spreadfactor=x['spreadfactor'])),
        stop=args.stop,
        checkpoint_freq=args.checkpoint_freq,
        checkpoint_at_end=args.checkpoint_at_end,
        keep_checkpoints_num=10, 
        checkpoint_score_attr="episode_reward_mean",
        restore=checkpoint,
        #export_formats=['model'],
        local_dir=args.local_dir
    )
