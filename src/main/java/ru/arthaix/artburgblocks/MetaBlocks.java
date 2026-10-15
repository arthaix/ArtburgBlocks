package ru.arthaix.artburgblocks;

import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import net.minecraft.block.SoundType;
import net.minecraft.block.material.MapColor;
import net.minecraft.block.material.Material;

/** The {@link BlockMeta} blocks listed in assets/artburgblocks/meta_blocks.json, which tools/gen_meta.py writes. */
final class MetaBlocks {
    private MetaBlocks() {
    }

    static List<BlockMeta> load() {
        List<BlockMeta> out = new ArrayList<>();
        try (InputStream in = MetaBlocks.class.getResourceAsStream("/assets/artburgblocks/meta_blocks.json")) {
            JsonArray all = new JsonParser().parse(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonArray();
            for (JsonElement e : all) {
                JsonObject o = e.getAsJsonObject();
                JsonArray ls = o.getAsJsonArray("looks");
                String[] looks = new String[ls.size()];
                for (int i = 0; i < looks.length; i++) {
                    looks[i] = ls.get(i).getAsString();
                }
                String name = o.get("name").getAsString();
                Material material = material(o.get("material").getAsString());
                MapColor map = mapColor(o.get("map").getAsString());
                SoundType sound = sound(o.get("sound").getAsString());
                float hardness = o.get("hardness").getAsFloat();
                boolean cutout = o.has("cutout") && o.get("cutout").getAsBoolean();
                out.add(cutout ? new BlockMetaCutout(name, material, map, sound, hardness, looks)
                        : new BlockMeta(name, material, map, sound, hardness, looks));
            }
        } catch (Exception ex) {
            throw new IllegalStateException("Artburg Blocks: cannot read meta_blocks.json", ex);
        }
        return out;
    }

    private static Material material(String s) {
        switch (s) {
            case "iron": return Material.IRON;
            case "glass": return Material.GLASS;
            case "wood": return Material.WOOD;
            default: return Material.ROCK;
        }
    }

    private static SoundType sound(String s) {
        switch (s) {
            case "metal": return SoundType.METAL;
            case "glass": return SoundType.GLASS;
            case "wood": return SoundType.WOOD;
            default: return SoundType.STONE;
        }
    }

    private static MapColor mapColor(String s) {
        switch (s) {
            case "red": return MapColor.RED;
            case "brown": return MapColor.BROWN;
            case "sand": return MapColor.SAND;
            case "snow": return MapColor.SNOW;
            case "black": return MapColor.BLACK;
            case "gray": return MapColor.GRAY;
            case "silver": return MapColor.SILVER;
            case "blue": return MapColor.BLUE;
            case "iron": return MapColor.IRON;
            case "green": return MapColor.GREEN;
            default: return MapColor.STONE;
        }
    }
}
