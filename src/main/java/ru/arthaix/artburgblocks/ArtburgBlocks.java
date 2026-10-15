package ru.arthaix.artburgblocks;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.block.Block;
import net.minecraft.block.material.MapColor;
import net.minecraft.client.renderer.block.model.ModelResourceLocation;
import net.minecraft.creativetab.CreativeTabs;
import net.minecraft.item.Item;
import net.minecraft.item.ItemBlock;
import net.minecraft.item.ItemStack;
import net.minecraftforge.client.event.ModelRegistryEvent;
import net.minecraftforge.client.model.ModelLoader;
import net.minecraftforge.event.RegistryEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.relauncher.Side;
import net.minecraftforge.fml.relauncher.SideOnly;

/** Blocks of the Artburg server. Needed on the server and on every client. */
@Mod(modid = ArtburgBlocks.MODID, name = "Artburg Blocks", version = ArtburgBlocks.VERSION, acceptedMinecraftVersions = "[1.12.2]")
@Mod.EventBusSubscriber(modid = ArtburgBlocks.MODID)
public class ArtburgBlocks {
    public static final String MODID = "artburgblocks";
    public static final String VERSION = "1.2.0";

    public static final List<Block> BLOCKS = new ArrayList<>();

    public static final CreativeTabs TAB = new CreativeTabs(MODID) {
        @Override
        public ItemStack createIcon() {
            return new ItemStack(BLOCKS.get(0));
        }
    };

    static {
        // the order is the order in the creative tab
        add(new BlockLawnAxis("lawn_sod", MapColor.GRASS));
        add(new BlockLawn("lawn_mowed", MapColor.GRASS));
        add(new BlockLawnStriped("lawn_striped", MapColor.GRASS));
        add(new BlockLawn("lawn_overgrown", MapColor.GRASS));
        add(new BlockLawn("lawn_dry", MapColor.SAND));
        add(new BlockLawn("lawn_worn", MapColor.GRASS));
        add(new BlockLawn("lawn_seeded", MapColor.DIRT));
        add(new BlockLawn("lawn_grid", MapColor.GRASS));
        for (int percent : new int[] {60, 70, 80, 90, 110, 120}) {     // tools/gen_granite.py makes their textures
            add(new BlockGranite(percent));
        }
        // tools/gen_asphalt.py makes their textures; plain "asphalt" matches the grey concrete of the existing roads
        add(new BlockAsphalt("asphalt_fresh", MapColor.BLACK));
        add(new BlockAsphalt("asphalt_new", MapColor.BLACK));
        add(new BlockAsphalt("asphalt", MapColor.GRAY));
        add(new BlockAsphalt("asphalt_worn", MapColor.GRAY));
        add(new BlockAsphalt("asphalt_old", MapColor.STONE));
        add(new BlockAsphalt("asphalt_patched", MapColor.GRAY));
        add(new BlockAsphalt("asphalt_sealed", MapColor.STONE));
        // road marking paint, wear in the metadata (BlockMarking.Wear)
        add(new BlockMarking("white", MapColor.SNOW));
        add(new BlockMarking("yellow", MapColor.YELLOW));
        add(new BlockMarking("orange", MapColor.ADOBE));
        add(new BlockMarking("blue", MapColor.BLUE));
        add(new BlockMarking("red", MapColor.RED));
    }

    private static void add(Block block) {
        BLOCKS.add(block);
    }

    @SubscribeEvent
    public static void registerBlocks(RegistryEvent.Register<Block> event) {
        for (Block block : BLOCKS) {
            event.getRegistry().register(block);
        }
    }

    @SubscribeEvent
    public static void registerItems(RegistryEvent.Register<Item> event) {
        for (Block block : BLOCKS) {
            event.getRegistry().register(block instanceof BlockMarking ? new ItemMarking((BlockMarking) block)
                    : new ItemBlock(block).setRegistryName(block.getRegistryName()));
        }
    }

    @SideOnly(Side.CLIENT)
    @SubscribeEvent
    public static void registerModels(ModelRegistryEvent event) {
        for (Block block : BLOCKS) {
            Item item = Item.getItemFromBlock(block);
            if (block instanceof BlockMarking) {          // one item per wear, drawn with that wear's block model
                for (BlockMarking.Wear w : BlockMarking.Wear.values()) {
                    ModelLoader.setCustomModelResourceLocation(item, w.ordinal(),
                            new ModelResourceLocation(block.getRegistryName(), "wear=" + w.getName()));
                }
            } else {
                ModelLoader.setCustomModelResourceLocation(item, 0, new ModelResourceLocation(block.getRegistryName(), "inventory"));
            }
        }
    }
}
