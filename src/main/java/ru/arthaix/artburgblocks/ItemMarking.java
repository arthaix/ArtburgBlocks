package ru.arthaix.artburgblocks;

import net.minecraft.item.ItemBlock;
import net.minecraft.item.ItemStack;

/** The item of a marking block: one item per wear, named after it (tile.artburgblocks.marking_white.fresh.name). */
public class ItemMarking extends ItemBlock {

    public ItemMarking(BlockMarking block) {
        super(block);
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
        BlockMarking.Wear[] all = BlockMarking.Wear.values();
        int meta = stack.getMetadata();
        return super.getTranslationKey(stack) + "." + all[meta >= 0 && meta < all.length ? meta : 0].getName();
    }
}
