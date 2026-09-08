checkpoint_dir=$1

landlord_path=$landlord_dir`ls -v "$checkpoint_dir"landlord_weights* | tail -1`
landlord_down1_path=$landlord_down1_dir`ls -v "$checkpoint_dir"landlord_down1_weights* | tail -1`
landlord_down2_path=$landlord_down2_dir`ls -v "$checkpoint_dir"landlord_down2_weights* | tail -1`
landlord_down3_path=$landlord_down3_dir`ls -v "$checkpoint_dir"landlord_down3_weights* | tail -1`

echo $landlord_path
echo $landlord_down1_path
echo $landlord_down2_path
echo $landlord_down3_path

mkdir -p most_recent_model

cp $landlord_path most_recent_model/landlord.ckpt
cp $landlord_down1_path most_recent_model/landlord_down1.ckpt
cp $landlord_down2_path most_recent_model/landlord_down2.ckpt
cp $landlord_down3_path most_recent_model/landlord_down3.ckpt
