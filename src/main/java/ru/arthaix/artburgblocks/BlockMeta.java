package ru.arthaix.artburgblocks;

import net.minecraft.block.Block;
import net.minecraft.block.SoundType;
import net.minecraft.block.material.MapColor;
import net.minecraft.block.material.Material;
import net.minecraft.block.properties.PropertyInteger;
import net.minecraft.block.state.BlockStateContainer;
import net.minecraft.block.state.IBlockState;
import net.minecraft.creativetab.CreativeTabs;
import net.minecraft.item.ItemStack;
import net.minecraft.util.NonNullList;

/**
 * A plain full block with up to 16 looks (shades, colours, states) in its metadata, one item for each. Chisels &amp;
 * Bits and LittleTiles keep the metadata, so every look works in bits and tiles too. The looks are named for the item
 * names (tile.artburgblocks.&lt;block&gt;.&lt;look&gt;.name); models are the blockstate variants "v=0".."v=15", written
 * by the texture generators in tools/.
 */
public class BlockMeta extends Block {
    public static final PropertyInteger V = PropertyInteger.create("v", 0, 15);

    private final String[] looks;

    public BlockMeta(String name, Material material, MapColor color, SoundType sound, float hardness, String... looks) {
        super(material, color);
        this.looks = looks;
        setRegistryName(ArtburgBlocks.MODID, name);
        setTranslationKey(ArtburgBlocks.MODID + "." + name);
        setHardness(hardness);
        setSoundType(sound);
        setCreativeTab(ArtburgBlocks.TAB);
        setDefaultState(blockState.getBaseState().withProperty(V, 0));
    }

    public int looks() {
        return looks.length;
    }

    public String look(int meta) {
        return looks[meta >= 0 && meta < looks.length ? meta : 0];
    }

    @Override
    protected BlockStateContainer createBlockState() {
        return new BlockStateContainer(this, V);
    }

    @Override
    public IBlockState getStateFromMeta(int meta) {
        return getDefaultState().withProperty(V, meta & 15);
    }

    @Override
    public int getMetaFromState(IBlockState state) {
        return state.getValue(V);
    }

    @Override
    public int damageDropped(IBlockState state) {
        return getMetaFromState(state);
    }

    @Override
    public void getSubBlocks(CreativeTabs tab, NonNullList<ItemStack> items) {
        for (int i = 0; i < looks.length; i++) {
            items.add(new ItemStack(this, 1, i));
        }
    }
}
