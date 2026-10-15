package ru.arthaix.artburgblocks;

import net.minecraft.block.material.MapColor;
import net.minecraft.block.properties.PropertyEnum;
import net.minecraft.block.state.BlockStateContainer;
import net.minecraft.block.state.IBlockState;
import net.minecraft.entity.EntityLivingBase;
import net.minecraft.util.EnumFacing;
import net.minecraft.util.Rotation;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.World;

/** Turf with a direction (rolls of sod, mowing lanes): it runs the way the player looks while placing it. */
public class BlockLawnAxis extends BlockLawn {
    public static final PropertyEnum<EnumFacing.Axis> AXIS =
            PropertyEnum.create("axis", EnumFacing.Axis.class, EnumFacing.Axis.X, EnumFacing.Axis.Z);

    public BlockLawnAxis(String name, MapColor color) {
        super(name, color);
        setDefaultState(blockState.getBaseState().withProperty(AXIS, EnumFacing.Axis.Z));
    }

    @Override
    protected BlockStateContainer createBlockState() {
        return new BlockStateContainer(this, AXIS);
    }

    @Override
    public IBlockState getStateForPlacement(World world, BlockPos pos, EnumFacing facing, float hitX, float hitY, float hitZ,
                                            int meta, EntityLivingBase placer) {
        return getDefaultState().withProperty(AXIS, placer.getHorizontalFacing().getAxis());
    }

    @Override
    public IBlockState getStateFromMeta(int meta) {
        return getDefaultState().withProperty(AXIS, (meta & 1) == 1 ? EnumFacing.Axis.X : EnumFacing.Axis.Z);
    }

    @Override
    public int getMetaFromState(IBlockState state) {
        return state.getValue(AXIS) == EnumFacing.Axis.X ? 1 : 0;
    }

    @Override
    public IBlockState withRotation(IBlockState state, Rotation rot) {
        if (rot == Rotation.CLOCKWISE_90 || rot == Rotation.COUNTERCLOCKWISE_90) {
            return state.withProperty(AXIS, state.getValue(AXIS) == EnumFacing.Axis.X ? EnumFacing.Axis.Z : EnumFacing.Axis.X);
        }
        return state;
    }
}
