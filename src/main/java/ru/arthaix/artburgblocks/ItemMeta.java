package ru.arthaix.artburgblocks;

import net.minecraft.item.ItemBlock;
import net.minecraft.item.ItemStack;

/** The item of a {@link BlockMeta}: one per look, named after it (tile.artburgblocks.clinker_basket.terracotta.name). */
public class ItemMeta extends ItemBlock {
    private final BlockMeta meta;

    public ItemMeta(BlockMeta block) {
        super(block);
        this.meta = block;
        setHasSubtypes(true);
        setMaxDamage(0);
        setRegistryName(block.getRegistryName());
    }

    @Override
    public int getMetadata(int damage) {
        return damage;
    }

    @Override
    public String getTranslationKey(ItemStack stack) {
        return super.getTranslationKey(stack) + "." + meta.look(stack.getMetadata());
    }
}
