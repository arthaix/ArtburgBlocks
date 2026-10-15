package ru.arthaix.artburgblocks;

import net.minecraft.block.Block;
import net.minecraft.block.SoundType;
import net.minecraft.block.material.MapColor;
import net.minecraft.block.material.Material;

/**
 * SBM's white granite (sbm:belygranit) in another brightness. Same material, hardness, resistance and sound as the
 * original; the texture is the original's made lighter or darker by tools/gen_granite.py.
 */
public class BlockGranite extends Block {

    /** @param percent brightness against the original, 100 = sbm:belygranit */
    public BlockGranite(int percent) {
        super(Material.ROCK, percent <= 70 ? MapColor.GRAY : percent <= 100 ? MapColor.STONE : MapColor.SILVER);
        String name = "belygranit_" + percent;
        setRegistryName(ArtburgBlocks.MODID, name);
        setTranslationKey(ArtburgBlocks.MODID + "." + name);
        setHardness(1.0F);
        setResistance(10.0F);
        setSoundType(SoundType.STONE);
        setCreativeTab(ArtburgBlocks.TAB);
    }
}
