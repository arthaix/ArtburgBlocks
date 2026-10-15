package ru.arthaix.artburgblocks;

import net.minecraft.block.Block;
import net.minecraft.block.SoundType;
import net.minecraft.block.material.MapColor;
import net.minecraft.block.material.Material;
import net.minecraft.block.state.IBlockState;
import net.minecraft.util.BlockRenderLayer;
import net.minecraft.util.EnumFacing;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.IBlockAccess;
import net.minecraftforge.common.EnumPlantType;
import net.minecraftforge.common.IPlantable;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

/**
 * A full block of turf in its own colours (no biome tint). Unlike vanilla grass it never spreads and never dies back
 * to dirt, so a lawn stays exactly as it was laid. Flowers, saplings and tall grass can be planted on it.
 */
public class BlockLawn extends Block {

    public BlockLawn(String name, MapColor color) {
        super(Material.GRASS, color);
        setRegistryName(ArtburgBlocks.MODID, name);
        setTranslationKey(ArtburgBlocks.MODID + "." + name);
        setHardness(0.6F);
        setSoundType(SoundType.PLANT);
        setHarvestLevel("shovel", 0);
        setCreativeTab(ArtburgBlocks.TAB);
    }

    @Override
    public boolean canSustainPlant(IBlockState state, IBlockAccess world, BlockPos pos, EnumFacing direction, IPlantable plantable) {
        EnumPlantType type = plantable.getPlantType(world, pos.offset(direction));
        return direction == EnumFacing.UP && (type == EnumPlantType.Plains || type == EnumPlantType.Beach);
    }

    /** The sides are dirt with a turf edge drawn over it, which has see-through texels. */
    @SideOnly(Side.CLIENT)
    @Override
    public BlockRenderLayer getRenderLayer() {
        return BlockRenderLayer.CUTOUT_MIPPED;
    }
}
