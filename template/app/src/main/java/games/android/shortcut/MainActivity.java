package games.android.shortcut;

import android.app.Activity;
import android.content.Intent;
import android.content.ComponentName;
import android.content.Context;
import android.content.res.AssetManager;
import android.os.Bundle;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

import toBeModified.R;

public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        String gameName="ToBeModified";
        String gameType="ToBeModified";
        String emuName="ToBeModified";
        String emuClass="ToBeModified";
        String callAction="ToBeModified";
        String appDataDirname=getExternalCacheDir().toString()+"/";
        Intent intent = new Intent(this,Activity.class);
        intent.setComponent(new ComponentName(emuName,emuClass));
        String romFilename="ToBeModified";
        intent.putExtra("ROM",appDataDirname+romFilename);
        copyRom(romFilename, appDataDirname);
        intent.putExtra("LIBRETRO","ToBeModified");
        //intent.putExtra("CONFIGFILE", "/data/data/com.retroarch/files/retroarch.cfg");
        if (gameType=="nes") {
          String romFilename="rom.nes";
          intent.putExtra("ROM", appDataDirname+romFilename);
          copyRom(romFilename,appDataDirname);
          intent.putExtra("LIBRETRO", "/data/data/com.retroarch/cores/fceumm_libretro_android.so");
        } else if (gameType=="n64") {
          String romFilename="rom.n64";
          intent.putExtra("ROM", appDataDirname+romFilename);
          copyRom(romFilename,appDataDirname);
          intent.putExtra("LIBRETRO", "/data/data/com.retroarch/cores/parallel_n64_libretro_android.so");
        } else if (gameType=="arcade") {
          String romFilename=gameName+".zip";
          intent.putExtra("ROM", appDataDirname+romFilename);
          copyRom(romFilename,appDataDirname);
          intent.putExtra("LIBRETRO", "/data/data/com.retroarch/cores/mame2014_libretro_android.so");
        } else if (gameType=="segamd") {
          String romFilename="rom.bin";
          intent.putExtra("ROM", appDataDirname+romFilename);
          copyRom(romFilename,appDataDirname);
          intent.putExtra("LIBRETRO", "/data/data/com.retroarch/cores/genesis_plus_gx_libretro_android.so");
        }
        startActivity(intent);
        //finishAndRemoveTask();
        finish();
    }

    private void copyRom(String assetfname, String romfpath) {
    	if (!(new File(romfpath+assetfname).exists())) {
          AssetManager assetManager = getApplicationContext().getAssets();
          try {
              InputStream in = assetManager.open(assetfname);
              OutputStream out = new FileOutputStream(romfpath+assetfname);
              byte[] buffer = new byte[1024000];
              int read = in.read(buffer);
              while (read != -1) {
                out.write(buffer, 0, read);
                read = in.read(buffer);
              }
              in.close();
              in = null;
              out.flush();
              out.close();
              out = null;
          } catch (Exception e) {
            e.getMessage();
          }
    	}
    }
}
