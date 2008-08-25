*
{
    line-width: 1;
    line-color: #999;
    polygon-fill: #fff;
    
    /* point-file: url("purple-point.png"); */
    pattern-file: url("http://www.istockphoto.com/file_thumbview_approve/3055566/2/istockphoto_3055566_crazy_background.jpg");
}

*[zoom>=6][zoom<12]
{
    line-color: #f90;
}

*[zoom=12]
{
    line-color: #f0f;
}

*[zoom>12]
{
    line-color: #f00;
}

#world-borders[zoom<10] NAME
{
    text-face-name: "DejaVu Sans Book";
    text-size: 10;
    text-fill: #000;
    text-placement: point;
}

*[zoom>=10] FIPS
{
    text-face-name: "DejaVu Sans Book";
    text-size: 10;
    text-fill: #000;
    text-placement: point;
}
