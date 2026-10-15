package ru.arthaix.artburgblocks;

import net.minecraft.block.Block;
import net.minecraft.block.SoundType;
import net.minecraft.block.material.MapColor;
import net.minecraft.block.material.Material;
import net.minecraft.block.properties.PropertyEnum;
import net.minecraft.block.state.BlockStateContainer;
import net.minecraft.block.state.IBlockState;
import net.minecraft.creativetab.CreativeTabs;
import net.minecraft.item.ItemStack;
import net.minecraft.util.IStringSerializable;
import net.minecraft.util.NonNullList;

/**
 * Road marking paint of one colour as a full block, one block for every colour with its wear in the metadata, so a
 * Chisels &amp; Bits or LittleTiles road keeps its marking in any state. The worn paint shows the ordinary asphalt
 * through it and so sits on any of the asphalt kinds. Textures come from tools/gen_asphalt.py.
 */
public class BlockMarking extends Block {

    public enum Wear implements IStringSerializable {
        FRESH, NORMAL, WORN;

        @Override
        public String getName() {
            return name().toLowerCase();
        }
    }

    public static final PropertyEnum<Wear> WEAR = PropertyEnum.create("wear", Wear.class);

    public BlockMarking(String color, MapColor mapColor) {
        super(Material.ROCK, mapColor);
        String name = "marking_" + color;
        setRegistryName(ArtburgBlocks.MODID, name);
        setTranslationKey(ArtburgBlocks.MODID + "." + name);
        setHardness(1.8F);
        setSoundType(SoundType.STONE);
        setCreativeTab(ArtburgBlocks.TAB);
        setDefaultState(blockState.getBaseState().withProperty(WEAR, Wear.FRESH));
    }

    @Override
    protected BlockStateContainer createBlockState() {
        return new BlockStateContainer(this, WEAR);
    }

    @Override
    public IBlockState getStateFromMeta(int meta) {
        Wear[] all = Wear.values();
        return getDefaultState().withProperty(WEAR, all[meta < all.length ? meta : 0]);
    }

    @Override
    public int getMetaFromState(IBlockState state) {
        return state.getValue(WEAR).ordinal();
    }

    @Override
    public int damageDropped(IBlockState state) {
        return getMetaFromState(state);
    }

    @Override
    public void getSubBlocks(CreativeTabs tab, NonNullList<ItemStack> items) {
        for (Wear w : Wear.values()) {
            items.add(new ItemStack(this, 1, w.ordinal()));
        }
    }
}
