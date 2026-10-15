package ru.arthaix.artburgblocks;

import net.minecraft.block.material.MapColor;
import net.minecraft.block.properties.PropertyBool;
import net.minecraft.block.state.BlockStateContainer;
import net.minecraft.block.state.IBlockState;
import net.minecraft.util.EnumFacing;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.IBlockAccess;

/**
 * A lawn mown in lanes two blocks wide (one pass of a ride-on mower with a striping roller), light and dark in turn.
 * The shade is not stored: it follows from the position, so a whole lawn laid with one block comes out striped by itself.
 */
public class BlockLawnStriped extends BlockLawnAxis {
    public static final PropertyBool LIGHT = PropertyBool.create("light");
    /** width of one mowing lane in blocks */
    public static final int LANE = 2;

    public BlockLawnStriped(String name, MapColor color) {
        super(name, color);
        setDefaultState(getDefaultState().withProperty(LIGHT, false));
    }

    @Override
    protected BlockStateContainer createBlockState() {
        return new BlockStateContainer(this, AXIS, LIGHT);
    }

    @Override
    public IBlockState getActualState(IBlockState state, IBlockAccess world, BlockPos pos) {
        // lanes run along the axis, so they alternate across it
        int across = state.getValue(AXIS) == EnumFacing.Axis.Z ? pos.getX() : pos.getZ();
        return state.withProperty(LIGHT, (Math.floorDiv(across, LANE) & 1) == 0);
    }
}
