/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package volvis;

import com.jogamp.opengl.GL;
import com.jogamp.opengl.GL2;
import com.jogamp.opengl.util.texture.Texture;
import com.jogamp.opengl.util.texture.awt.AWTTextureIO;
import gui.RaycastRendererPanel;
import gui.TransferFunction2DEditor;
import gui.TransferFunctionEditor;
import java.awt.image.BufferedImage;
import util.TFChangeListener;
import util.VectorMath;
import volume.GradientVolume;
import volume.Volume;
import volume.VoxelGradient;

/**
 *
 * @author michel
 */
public class RaycastRenderer extends Renderer implements TFChangeListener {

    private Volume volume = null;
    private GradientVolume gradients = null;
    RaycastRendererPanel panel;
    TransferFunction tFunc;
    TransferFunctionEditor tfEditor;
    TransferFunction2DEditor tfEditor2D;
    
    String rayFunction = "slicer";
    
    public RaycastRenderer() {
        panel = new RaycastRendererPanel(this);
        panel.setSpeedLabel("0");
    }

    public void setVolume(Volume vol) {
        System.out.println("Assigning volume");
        volume = vol;

        System.out.println("Computing gradients");
        gradients = new GradientVolume(vol);

        // set up image for storing the resulting rendering
        // the image width and height are equal to the length of the volume diagonal
        int imageSize = (int) Math.floor(Math.sqrt(vol.getDimX() * vol.getDimX() + vol.getDimY() * vol.getDimY()
                + vol.getDimZ() * vol.getDimZ()));
        if (imageSize % 2 != 0) {
            imageSize = imageSize + 1;
        }
        image = new BufferedImage(imageSize, imageSize, BufferedImage.TYPE_INT_ARGB);
        // create a standard TF where lowest intensity maps to black, the highest to white, and opacity increases
        // linearly from 0.0 to 1.0 over the intensity range
        tFunc = new TransferFunction(volume.getMinimum(), volume.getMaximum());
        
        // uncomment this to initialize the TF with good starting values for the orange dataset 
        tFunc.setTestFunc();
        
        
        tFunc.addTFChangeListener(this);
        tfEditor = new TransferFunctionEditor(tFunc, volume.getHistogram());
        
        tfEditor2D = new TransferFunction2DEditor(volume, gradients);
        tfEditor2D.addTFChangeListener(this);

        System.out.println("Finished initialization of RaycastRenderer");
    }

    public RaycastRendererPanel getPanel() {
        return panel;
    }

    public TransferFunction2DEditor getTF2DPanel() {
        return tfEditor2D;
    }
    
    public TransferFunctionEditor getTFPanel() {
        return tfEditor;
    }
     

    short getVoxelOld(double[] coord) {

        if (coord[0] < 0 || coord[0] > volume.getDimX() || coord[1] < 0 || coord[1] > volume.getDimY()
                || coord[2] < 0 || coord[2] > volume.getDimZ()) {
            return 0;
        }

        int x = (int) Math.floor(coord[0]);
        int y = (int) Math.floor(coord[1]);
        int z = (int) Math.floor(coord[2]);

        return volume.getVoxel(x, y, z);
    }
    
    short getVoxel(double[] coord) {    // using Trilinear interpolation
    
        if (coord[0] < 0 || coord[0] > volume.getDimX() || coord[1] < 0 || coord[1] > volume.getDimY()
                || coord[2] < 0 || coord[2] > volume.getDimZ()) {
            return 0;
        }
        
        // derived from https://en.wikipedia.org/wiki/Trilinear_interpolation
        
        int x_0 = (int) Math.floor(coord[0]);
        int x_1 = (int) Math.ceil(coord[0]);
        int y_0 = (int) Math.floor(coord[1]);
        int y_1 = (int) Math.ceil(coord[1]);
        int z_0 = (int) Math.floor(coord[2]);
        int z_1 = (int) Math.ceil(coord[2]);
        
        // check if x_1, y_1 and z_1 are not outside the box
        if (x_1 >= volume.getDimX() || y_1 >= volume.getDimY() || z_1 >= volume.getDimZ() ) {
                return 0;
        }
          
        // voxels on intersects
        short c000 = volume.getVoxel(x_0, y_0, z_0);
        short c001 = volume.getVoxel(x_0, y_0, z_1);
        short c010 = volume.getVoxel(x_0, y_1, z_0);
        short c011 = volume.getVoxel(x_0, y_1, z_1);
        short c100 = volume.getVoxel(x_1, y_0, z_0);
        short c101 = volume.getVoxel(x_1, y_0, z_1);
        short c110 = volume.getVoxel(x_1, y_1, z_0);
        short c111 = volume.getVoxel(x_1, y_1, z_1);
        
        //compute differences between x, y, z and x0, y0, z0        
        double x_d = (coord[0]-x_0)/(x_1-x_0);
        double y_d = (coord[1]-y_0)/(y_1-y_0);
        double z_d = (coord[2]-z_0)/(z_1-z_0);
        
        //interpolate along x
        double c00 = c000 * (1 - x_d) + c100 * x_d;
        double c01 = c001 * (1 - x_d) + c101 * x_d;
        double c10 = c010 * (1 - x_d) + c110 * x_d;
        double c11 = c011 * (1 - x_d) + c111 * x_d;
        
        //interpolate along y
        double c0 = c00 * (1 - y_d) + c10 * y_d;
        double c1 = c01 * (1 - y_d) + c11 * y_d;
        
        //interpolate along z
        return (short) (c0 * (1 - z_d) + c1 * z_d);       
    }


    void slicer(double[] viewMatrix) {

        // clear image
        for (int j = 0; j < image.getHeight(); j++) {
            for (int i = 0; i < image.getWidth(); i++) {
                image.setRGB(i, j, 0);
            }
        }

        // vector uVec and vVec define a plane through the origin, 
        // perpendicular to the view vector viewVec
        double[] viewVec = new double[3];
        double[] uVec = new double[3];
        double[] vVec = new double[3];
        VectorMath.setVector(viewVec, viewMatrix[2], viewMatrix[6], viewMatrix[10]);
        VectorMath.setVector(uVec, viewMatrix[0], viewMatrix[4], viewMatrix[8]);
        VectorMath.setVector(vVec, viewMatrix[1], viewMatrix[5], viewMatrix[9]);

        // image is square
        int imageCenter = image.getWidth() / 2;

        double[] pixelCoord = new double[3];
        double[] volumeCenter = new double[3];
        VectorMath.setVector(volumeCenter, volume.getDimX() / 2, volume.getDimY() / 2, volume.getDimZ() / 2);

        // sample on a plane through the origin of the volume data
        double max = volume.getMaximum();
        TFColor voxelColor = new TFColor();

        
        for (int j = 0; j < image.getHeight(); j++) {
            for (int i = 0; i < image.getWidth(); i++) {
                pixelCoord[0] = uVec[0] * (i - imageCenter) + vVec[0] * (j - imageCenter)
                        + volumeCenter[0];
                pixelCoord[1] = uVec[1] * (i - imageCenter) + vVec[1] * (j - imageCenter)
                        + volumeCenter[1];
                pixelCoord[2] = uVec[2] * (i - imageCenter) + vVec[2] * (j - imageCenter)
                        + volumeCenter[2];

                int val = getVoxel(pixelCoord);
                
                // Map the intensity to a grey value by linear scaling
                voxelColor.r = val/max;
                voxelColor.g = voxelColor.r;
                voxelColor.b = voxelColor.r;
                voxelColor.a = val > 0 ? 1.0 : 0.0;  // this makes intensity 0 completely transparent and the rest opaque
                // Alternatively, apply the transfer function to obtain a color
                // voxelColor = tFunc.getColor(val);
                
                
                // BufferedImage expects a pixel color packed as ARGB in an int
                int c_alpha = voxelColor.a <= 1.0 ? (int) Math.floor(voxelColor.a * 255) : 255;
                int c_red = voxelColor.r <= 1.0 ? (int) Math.floor(voxelColor.r * 255) : 255;
                int c_green = voxelColor.g <= 1.0 ? (int) Math.floor(voxelColor.g * 255) : 255;
                int c_blue = voxelColor.b <= 1.0 ? (int) Math.floor(voxelColor.b * 255) : 255;
                int pixelColor = (c_alpha << 24) | (c_red << 16) | (c_green << 8) | c_blue;
                image.setRGB(i, j, pixelColor);
            }
        }

    }
    
    void mip(double[] viewMatrix) { //using MIP
        // clear image
        for (int j = 0; j < image.getHeight(); j++) {
            for (int i = 0; i < image.getWidth(); i++) {
                image.setRGB(i, j, 0);
            }
        }
         // vector uVec and vVec define a plane through the origin, 
        // perpendicular to the view vector viewVec
        double[] viewVec = new double[3];
        double[] uVec = new double[3];
        double[] vVec = new double[3];
        VectorMath.setVector(viewVec, viewMatrix[2], viewMatrix[6], viewMatrix[10]);
        VectorMath.setVector(uVec, viewMatrix[0], viewMatrix[4], viewMatrix[8]);
        VectorMath.setVector(vVec, viewMatrix[1], viewMatrix[5], viewMatrix[9]);

        // image is square
        int imageCenter = image.getWidth() / 2;

        double[] pixelCoord = new double[3];
        double[] volumeCenter = new double[3];
        VectorMath.setVector(volumeCenter, volume.getDimX() / 2, volume.getDimY() / 2, volume.getDimZ() / 2);

        // sample on a plane through the origin of the volume data
        double max = volume.getMaximum();
        TFColor voxelColor = new TFColor();
        
        int maximumDim = volume.getDimX();
        if (volume.getDimY() > maximumDim) {
            maximumDim = volume.getDimY();
        }
        if (volume.getDimZ() > maximumDim) {
            maximumDim = volume.getDimZ();
        }
        
        int stepsize = 1;
        if(this.interactiveMode) { // this means user is spinning the object
            stepsize = 2;
        }
        
        //implementing LMIP instead of MIP
        int threshold = (int) (0.95 * max); //threshold is 0.95 times the maximum intensity measured in volume

        for (int j = 0; j < image.getHeight(); j+=stepsize) {
            for (int i = 0; i < image.getWidth(); i+=stepsize) {
                int maxVoxel = 0;
                for (int k = -maximumDim; k < maximumDim; k++) {
                    pixelCoord[0] = uVec[0] * (i - imageCenter) + vVec[0] * (j - imageCenter)
                        + viewVec[0] * (k)+ volumeCenter[0];
                    pixelCoord[1] = uVec[1] * (i - imageCenter) + vVec[1] * (j - imageCenter)
                        + viewVec[1] * (k)+ volumeCenter[1];
                    pixelCoord[2] = uVec[2] * (i - imageCenter) + vVec[2] * (j - imageCenter)
                        + viewVec[2] * (k)+ volumeCenter[2];
                    int v = getVoxel(pixelCoord);
                    if (v > maxVoxel) {
                        maxVoxel = v;
                    }
                    if (maxVoxel > threshold) {
                        break;
                    }
                }
                
                int val = maxVoxel;
                // Map the intensity to a grey value by linear scaling
                voxelColor.r = val/max;
                voxelColor.g = voxelColor.r;
                voxelColor.b = voxelColor.r;
                voxelColor.a = val > 0 ? 1.0 : 0.0;  // this makes intensity 0 completely transparent and the rest opaque
                // Alternatively, apply the transfer function to obtain a color
                // voxelColor = tFunc.getColor(val);
                
                
                // BufferedImage expects a pixel color packed as ARGB in an int
                int c_alpha = voxelColor.a <= 1.0 ? (int) Math.floor(voxelColor.a * 255) : 255;
                int c_red = voxelColor.r <= 1.0 ? (int) Math.floor(voxelColor.r * 255) : 255;
                int c_green = voxelColor.g <= 1.0 ? (int) Math.floor(voxelColor.g * 255) : 255;
                int c_blue = voxelColor.b <= 1.0 ? (int) Math.floor(voxelColor.b * 255) : 255;
                int pixelColor = (c_alpha << 24) | (c_red << 16) | (c_green << 8) | c_blue;
                image.setRGB(i, j, pixelColor);
                
                if (stepsize == 2) {
                    image.setRGB(i+1, j, pixelColor);
                    image.setRGB(i, j+1, pixelColor);
                    image.setRGB(i+1, j+1, pixelColor);
                }
            }
        }

        
    }
    
    void compositing(double[] viewMatrix) { //using Compositing back-to-front
        // clear image
        for (int j = 0; j < image.getHeight(); j++) {
            for (int i = 0; i < image.getWidth(); i++) {
                image.setRGB(i, j, 0);
            }
        }
         // vector uVec and vVec define a plane through the origin, 
        // perpendicular to the view vector viewVec
        double[] viewVec = new double[3];
        double[] uVec = new double[3];
        double[] vVec = new double[3];
        VectorMath.setVector(viewVec, viewMatrix[2], viewMatrix[6], viewMatrix[10]);
        VectorMath.setVector(uVec, viewMatrix[0], viewMatrix[4], viewMatrix[8]);
        VectorMath.setVector(vVec, viewMatrix[1], viewMatrix[5], viewMatrix[9]);

        // image is square
        int imageCenter = image.getWidth() / 2;

        double[] pixelCoord = new double[3];
        double[] volumeCenter = new double[3];
        VectorMath.setVector(volumeCenter, volume.getDimX() / 2, volume.getDimY() / 2, volume.getDimZ() / 2);

        // sample on a plane through the origin of the volume data
        double max = volume.getMaximum();
        // TFColor voxelColor = new TFColor();
        
        int maximumDim = volume.getDimX();
        if (volume.getDimY() > maximumDim) {
            maximumDim = volume.getDimY();
        }
        if (volume.getDimZ() > maximumDim) {
            maximumDim = volume.getDimZ();
        }
        
        int stepsize = 1;
        if(this.interactiveMode) { // this means user is spinning the object
            stepsize = 2;
        }
        
        // Initialize sampleColor
        TFColor sampleColor;
        
        for (int j = 0; j < image.getHeight(); j+=stepsize) {
            for (int i = 0; i < image.getWidth(); i+=stepsize) {
                // Reset voxelColor
                TFColor voxelColor = new TFColor();
                for (int k = -maximumDim; k < maximumDim; k++) {
                    pixelCoord[0] = uVec[0] * (i - imageCenter) + vVec[0] * (j - imageCenter)
                        + viewVec[0] * (k)+ volumeCenter[0];
                    pixelCoord[1] = uVec[1] * (i - imageCenter) + vVec[1] * (j - imageCenter)
                        + viewVec[1] * (k)+ volumeCenter[1];
                    pixelCoord[2] = uVec[2] * (i - imageCenter) + vVec[2] * (j - imageCenter)
                        + viewVec[2] * (k)+ volumeCenter[2];
                    int val = getVoxel(pixelCoord);
                    sampleColor = tFunc.getColor(val);
                    voxelColor.r = sampleColor.a*sampleColor.r + (1 - sampleColor.a)*voxelColor.r;
                    voxelColor.g = sampleColor.a*sampleColor.g + (1 - sampleColor.a)*voxelColor.g;
                    voxelColor.b = sampleColor.a*sampleColor.b + (1 - sampleColor.a)*voxelColor.b;
                }
                
                // BufferedImage expects a pixel color packed as ARGB in an int
                int c_alpha = voxelColor.a <= 1.0 ? (int) Math.floor(voxelColor.a * 255) : 255;
                int c_red = voxelColor.r <= 1.0 ? (int) Math.floor(voxelColor.r * 255) : 255;
                int c_green = voxelColor.g <= 1.0 ? (int) Math.floor(voxelColor.g * 255) : 255;
                int c_blue = voxelColor.b <= 1.0 ? (int) Math.floor(voxelColor.b * 255) : 255;
                int pixelColor = (c_alpha << 24) | (c_red << 16) | (c_green << 8) | c_blue;
                image.setRGB(i, j, pixelColor);
                
                if (stepsize == 2) {
                image.setRGB(i+1, j, pixelColor);
                image.setRGB(i, j+1, pixelColor);
                image.setRGB(i+1, j+1, pixelColor);
                }
            }
        }

        
    }

        void compositingERT(double[] viewMatrix) { //using Compositing with early ray termination
        // clear image
        for (int j = 0; j < image.getHeight(); j++) {
            for (int i = 0; i < image.getWidth(); i++) {
                image.setRGB(i, j, 0);
            }
        }
         // vector uVec and vVec define a plane through the origin, 
        // perpendicular to the view vector viewVec
        double[] viewVec = new double[3];
        double[] uVec = new double[3];
        double[] vVec = new double[3];
        VectorMath.setVector(viewVec, viewMatrix[2], viewMatrix[6], viewMatrix[10]);
        VectorMath.setVector(uVec, viewMatrix[0], viewMatrix[4], viewMatrix[8]);
        VectorMath.setVector(vVec, viewMatrix[1], viewMatrix[5], viewMatrix[9]);

        // image is square
        int imageCenter = image.getWidth() / 2;

        double[] pixelCoord = new double[3];
        double[] volumeCenter = new double[3];
        VectorMath.setVector(volumeCenter, volume.getDimX() / 2, volume.getDimY() / 2, volume.getDimZ() / 2);

        // sample on a plane through the origin of the volume data
        double max = volume.getMaximum();
        // TFColor voxelColor = new TFColor();
        
        int maximumDim = volume.getDimX();
        if (volume.getDimY() > maximumDim) {
            maximumDim = volume.getDimY();
        }
        if (volume.getDimZ() > maximumDim) {
            maximumDim = volume.getDimZ();
        }
        
        int stepsize = 1;
        if(this.interactiveMode) { // this means user is spinning the object
            stepsize = 2;
        }
        
        // Initialize sampleColor and composite transparency
        TFColor sampleColor;
        double compTransparancy;
        
        for (int j = 0; j < image.getHeight(); j+=stepsize) {
            for (int i = 0; i < image.getWidth(); i+=stepsize) {
                // Reset voxelColor
                compTransparancy = 1;
                TFColor voxelColor = new TFColor();
                voxelColor.r = 0;
                voxelColor.g = 0;
                voxelColor.b = 0;
                for (int k = maximumDim; k > -maximumDim; k--) {    //switched order in loop
                    
                    pixelCoord[0] = uVec[0] * (i - imageCenter) + vVec[0] * (j - imageCenter)
                        + viewVec[0] * (k)+ volumeCenter[0];
                    pixelCoord[1] = uVec[1] * (i - imageCenter) + vVec[1] * (j - imageCenter)
                        + viewVec[1] * (k)+ volumeCenter[1];
                    pixelCoord[2] = uVec[2] * (i - imageCenter) + vVec[2] * (j - imageCenter)
                        + viewVec[2] * (k)+ volumeCenter[2];
                    int val = getVoxel(pixelCoord);
                    sampleColor = tFunc.getColor(val);

                    voxelColor.r = voxelColor.r + sampleColor.a * sampleColor.r * compTransparancy;
                    voxelColor.g = voxelColor.g + sampleColor.a * sampleColor.g * compTransparancy;
                    voxelColor.b = voxelColor.b + sampleColor.a * sampleColor.b * compTransparancy;
                    compTransparancy = compTransparancy * (1 - sampleColor.a);
                    
                    if (compTransparancy < 0.05) {
                        break;
                    }

                }
                
                // BufferedImage expects a pixel color packed as ARGB in an int
                int c_alpha = voxelColor.a <= 1.0 ? (int) Math.floor(voxelColor.a * 255) : 255;
                int c_red = voxelColor.r <= 1.0 ? (int) Math.floor(voxelColor.r * 255) : 255;
                int c_green = voxelColor.g <= 1.0 ? (int) Math.floor(voxelColor.g * 255) : 255;
                int c_blue = voxelColor.b <= 1.0 ? (int) Math.floor(voxelColor.b * 255) : 255;
                int pixelColor = (c_alpha << 24) | (c_red << 16) | (c_green << 8) | c_blue;
                image.setRGB(i, j, pixelColor);
                
                if (stepsize == 2) {
                image.setRGB(i+1, j, pixelColor);
                image.setRGB(i, j+1, pixelColor);
                image.setRGB(i+1, j+1, pixelColor);
                }
            }
        }

        
    }

    void transfer2d(double[] viewMatrix) { //using 2d transfer function
        // clear image
        for (int j = 0; j < image.getHeight(); j++) {
            for (int i = 0; i < image.getWidth(); i++) {
                image.setRGB(i, j, 0);
            }
        }
         // vector uVec and vVec define a plane through the origin, 
        // perpendicular to the view vector viewVec
        double[] viewVec = new double[3];
        double[] uVec = new double[3];
        double[] vVec = new double[3];
        VectorMath.setVector(viewVec, viewMatrix[2], viewMatrix[6], viewMatrix[10]);
        VectorMath.setVector(uVec, viewMatrix[0], viewMatrix[4], viewMatrix[8]);
        VectorMath.setVector(vVec, viewMatrix[1], viewMatrix[5], viewMatrix[9]);

        // image is square
        int imageCenter = image.getWidth() / 2;

        double[] pixelCoord = new double[3];
        double[] volumeCenter = new double[3];
        VectorMath.setVector(volumeCenter, volume.getDimX() / 2, volume.getDimY() / 2, volume.getDimZ() / 2);

        // get baseIntensity, radius, and color from triangleWidget
        double baseIntensity = tfEditor2D.triangleWidget.baseIntensity;
        double radius = tfEditor2D.triangleWidget.radius;
        double r = tfEditor2D.triangleWidget.color.r;
        double g = tfEditor2D.triangleWidget.color.g;                    
        double b = tfEditor2D.triangleWidget.color.b;
        double a = tfEditor2D.triangleWidget.color.a;


        // sample on a plane through the origin of the volume data
        
        int maximumDim = volume.getDimX();
        if (volume.getDimY() > maximumDim) {
            maximumDim = volume.getDimY();
        }
        if (volume.getDimZ() > maximumDim) {
            maximumDim = volume.getDimZ();
        }
        
        int stepsize = 1;
        if(this.interactiveMode) { // this means user is spinning the object
            stepsize = 2;
        }
       

        for (int j = 0; j < image.getHeight(); j+=stepsize) {
            for (int i = 0; i < image.getWidth(); i+=stepsize) {
                // Reset voxelColor
                TFColor voxelColor = new TFColor(r,g,b,0);

                for (int k = maximumDim; k < -maximumDim; k--) {
                    pixelCoord[0] = uVec[0] * (i - imageCenter) + vVec[0] * (j - imageCenter)
                        + viewVec[0] * (k)+ volumeCenter[0];
                    pixelCoord[1] = uVec[1] * (i - imageCenter) + vVec[1] * (j - imageCenter)
                        + viewVec[1] * (k)+ volumeCenter[1];
                    pixelCoord[2] = uVec[2] * (i - imageCenter) + vVec[2] * (j - imageCenter)
                        + viewVec[2] * (k)+ volumeCenter[2];

                    // get intensity of voxel by trilinear interpolation
                    int val = getVoxel(pixelCoord);

                    // Determine opacity of voxel
                    double opacity = 0;
                   // VoxelGradient gradient = VoxelGradient(x,y,z); //get gradient
                    VoxelGradient gradient = gradients.getGradient((int) pixelCoord[0], (int) pixelCoord[1], (int) pixelCoord[2]);



                    if(gradient.mag == 0 && val == baseIntensity){
                        opacity = a; // opacity is 1 * alpha_v
                    } else if(gradient.mag > 0 
                        && ((val - (radius * gradient.mag)) <= baseIntensity)
                        && (baseIntensity <= (val + radius * gradient.mag))){
                        opacity = a*(1 - 1/radius*((baseIntensity - val)/gradient.mag));
                    } else {
                        opacity = 0;
                    }

                    // update voxel opacity
                    voxelColor.a = voxelColor.a + (1 - opacity);
                }
                
                // BufferedImage expects a pixel color packed as ARGB in an int
                int c_alpha = voxelColor.a <= 1.0 ? (int) Math.floor(voxelColor.a * 255) : 255;
                int c_red = voxelColor.r <= 1.0 ? (int) Math.floor(voxelColor.r * 255) : 255;
                int c_green = voxelColor.g <= 1.0 ? (int) Math.floor(voxelColor.g * 255) : 255;
                int c_blue = voxelColor.b <= 1.0 ? (int) Math.floor(voxelColor.b * 255) : 255;
                int pixelColor = (c_alpha << 24) | (c_red << 16) | (c_green << 8) | c_blue;
                image.setRGB(i, j, pixelColor);
                
                if (stepsize == 2) {
                image.setRGB(i+1, j, pixelColor);
                image.setRGB(i, j+1, pixelColor);
                image.setRGB(i+1, j+1, pixelColor);
                }
            }
        }

        
    }


    private void drawBoundingBox(GL2 gl) {
        gl.glPushAttrib(GL2.GL_CURRENT_BIT);
        gl.glDisable(GL2.GL_LIGHTING);
        gl.glColor4d(1.0, 1.0, 1.0, 1.0);
        gl.glLineWidth(1.5f);
        gl.glEnable(GL.GL_LINE_SMOOTH);
        gl.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST);
        gl.glEnable(GL.GL_BLEND);
        gl.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);

        gl.glBegin(GL.GL_LINE_LOOP);
        gl.glVertex3d(-volume.getDimX() / 2.0, -volume.getDimY() / 2.0, volume.getDimZ() / 2.0);
        gl.glVertex3d(-volume.getDimX() / 2.0, volume.getDimY() / 2.0, volume.getDimZ() / 2.0);
        gl.glVertex3d(volume.getDimX() / 2.0, volume.getDimY() / 2.0, volume.getDimZ() / 2.0);
        gl.glVertex3d(volume.getDimX() / 2.0, -volume.getDimY() / 2.0, volume.getDimZ() / 2.0);
        gl.glEnd();

        gl.glBegin(GL.GL_LINE_LOOP);
        gl.glVertex3d(-volume.getDimX() / 2.0, -volume.getDimY() / 2.0, -volume.getDimZ() / 2.0);
        gl.glVertex3d(-volume.getDimX() / 2.0, volume.getDimY() / 2.0, -volume.getDimZ() / 2.0);
        gl.glVertex3d(volume.getDimX() / 2.0, volume.getDimY() / 2.0, -volume.getDimZ() / 2.0);
        gl.glVertex3d(volume.getDimX() / 2.0, -volume.getDimY() / 2.0, -volume.getDimZ() / 2.0);
        gl.glEnd();

        gl.glBegin(GL.GL_LINE_LOOP);
        gl.glVertex3d(volume.getDimX() / 2.0, -volume.getDimY() / 2.0, -volume.getDimZ() / 2.0);
        gl.glVertex3d(volume.getDimX() / 2.0, -volume.getDimY() / 2.0, volume.getDimZ() / 2.0);
        gl.glVertex3d(volume.getDimX() / 2.0, volume.getDimY() / 2.0, volume.getDimZ() / 2.0);
        gl.glVertex3d(volume.getDimX() / 2.0, volume.getDimY() / 2.0, -volume.getDimZ() / 2.0);
        gl.glEnd();

        gl.glBegin(GL.GL_LINE_LOOP);
        gl.glVertex3d(-volume.getDimX() / 2.0, -volume.getDimY() / 2.0, -volume.getDimZ() / 2.0);
        gl.glVertex3d(-volume.getDimX() / 2.0, -volume.getDimY() / 2.0, volume.getDimZ() / 2.0);
        gl.glVertex3d(-volume.getDimX() / 2.0, volume.getDimY() / 2.0, volume.getDimZ() / 2.0);
        gl.glVertex3d(-volume.getDimX() / 2.0, volume.getDimY() / 2.0, -volume.getDimZ() / 2.0);
        gl.glEnd();

        gl.glBegin(GL.GL_LINE_LOOP);
        gl.glVertex3d(-volume.getDimX() / 2.0, volume.getDimY() / 2.0, -volume.getDimZ() / 2.0);
        gl.glVertex3d(-volume.getDimX() / 2.0, volume.getDimY() / 2.0, volume.getDimZ() / 2.0);
        gl.glVertex3d(volume.getDimX() / 2.0, volume.getDimY() / 2.0, volume.getDimZ() / 2.0);
        gl.glVertex3d(volume.getDimX() / 2.0, volume.getDimY() / 2.0, -volume.getDimZ() / 2.0);
        gl.glEnd();

        gl.glBegin(GL.GL_LINE_LOOP);
        gl.glVertex3d(-volume.getDimX() / 2.0, -volume.getDimY() / 2.0, -volume.getDimZ() / 2.0);
        gl.glVertex3d(-volume.getDimX() / 2.0, -volume.getDimY() / 2.0, volume.getDimZ() / 2.0);
        gl.glVertex3d(volume.getDimX() / 2.0, -volume.getDimY() / 2.0, volume.getDimZ() / 2.0);
        gl.glVertex3d(volume.getDimX() / 2.0, -volume.getDimY() / 2.0, -volume.getDimZ() / 2.0);
        gl.glEnd();

        gl.glDisable(GL.GL_LINE_SMOOTH);
        gl.glDisable(GL.GL_BLEND);
        gl.glEnable(GL2.GL_LIGHTING);
        gl.glPopAttrib();

    }

    public void setRayFunction (String rayFunction) {
        this.rayFunction = rayFunction;
    }
    
    @Override
    public void visualize(GL2 gl) {

        if (volume == null) {
            return;
        }

        drawBoundingBox(gl);

        gl.glGetDoublev(GL2.GL_MODELVIEW_MATRIX, viewMatrix, 0);

        long startTime = System.currentTimeMillis();
        if (rayFunction.equals("slicer")) {
            slicer(viewMatrix);
        }
        else if (rayFunction.equals("mip")) {
            mip(viewMatrix);
        }
        else if (rayFunction.equals("compositing")) {
            compositing(viewMatrix);
        } 
        else if (rayFunction.equals("transfer2d")){
            transfer2d(viewMatrix);
        }
        
        long endTime = System.currentTimeMillis();
        double runningTime = (endTime - startTime);
        panel.setSpeedLabel(Double.toString(runningTime));

        Texture texture = AWTTextureIO.newTexture(gl.getGLProfile(), image, false);

        gl.glPushAttrib(GL2.GL_LIGHTING_BIT);
        gl.glDisable(GL2.GL_LIGHTING);
        gl.glEnable(GL.GL_BLEND);
        gl.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);

        // draw rendered image as a billboard texture
        texture.enable(gl);
        texture.bind(gl);
        double halfWidth = image.getWidth() / 2.0;
        gl.glPushMatrix();
        gl.glLoadIdentity();
        gl.glBegin(GL2.GL_QUADS);
        gl.glColor4f(1.0f, 1.0f, 1.0f, 1.0f);
        gl.glTexCoord2d(0.0, 0.0);
        gl.glVertex3d(-halfWidth, -halfWidth, 0.0);
        gl.glTexCoord2d(0.0, 1.0);
        gl.glVertex3d(-halfWidth, halfWidth, 0.0);
        gl.glTexCoord2d(1.0, 1.0);
        gl.glVertex3d(halfWidth, halfWidth, 0.0);
        gl.glTexCoord2d(1.0, 0.0);
        gl.glVertex3d(halfWidth, -halfWidth, 0.0);
        gl.glEnd();
        texture.disable(gl);
        texture.destroy(gl);
        gl.glPopMatrix();

        gl.glPopAttrib();


        if (gl.glGetError() > 0) {
            System.out.println("some OpenGL error: " + gl.glGetError());
        }

    }
    private BufferedImage image;
    private double[] viewMatrix = new double[4 * 4];

    @Override
    public void changed() {
        for (int i=0; i < listeners.size(); i++) {
            listeners.get(i).changed();
        }
    }
}
