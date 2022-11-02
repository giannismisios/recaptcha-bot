import cv2
def split_image(image_path, dimension):
    img = cv2.imread(image_path)

    im_height = img.shape[0]
    im_width = img.shape[1]

    tile_height = im_height//dimension
    tile_width = im_width//dimension
    tiles = []
    for y in range(0,tile_height*dimension,tile_height):
        for x in range(0,tile_width*dimension,tile_width):
            y1 = y + tile_height
            x1 = x + tile_width
            tile = img[y:y1,x:x1]
            tiles.append(tile)
            cv2.imwrite('images/'+str(x)+str(y)+'.png',tile)
    return tiles
