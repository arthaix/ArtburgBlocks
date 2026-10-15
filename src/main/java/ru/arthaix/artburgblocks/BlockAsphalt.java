package ru.arthaix.artburgblocks;

import net.minecraft.block.Block;
import net.minecraft.block.SoundType;
import net.minecraft.block.material.MapColor;
import net.minecraft.block.material.Material;

/**
 * A full block of asphalt. Hard and loud like the grey concrete the roads were made of until now, so it can stand in
 * for it, also as Chisels &amp; Bits bits and LittleTiles tiles. Textures come from tools/gen_asphalt.py.
 */
public class BlockAsphalt extends Block {

    public BlockAsphalt(String name, MapColor color) {
        super(Material.ROCK, color);
        setRegistryName(ArtburgBlocks.MODID, name);
        setTranslationKey(ArtburgBlocks.MODID + "." + name);
        setHardness(1.8F);
        setSoundType(SoundType.STONE);
        setCreativeTab(ArtburgBlocks.TAB);
    }
}
