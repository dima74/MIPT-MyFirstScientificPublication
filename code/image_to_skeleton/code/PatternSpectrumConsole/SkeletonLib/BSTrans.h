#pragma once

#include "BitRaster.h"
#include "LinkedList.h"
#include "SpanTree.h"
#include "StructureSkel.h"
#include "StructureTD.h"
#include "TriDel.h"

/*
Подпрограмма гранично-скелетного преобразования осуществляет построение
граничных контуров и скелета. Контура, ограничивающие площадь менее
AreaIgnore, уничтожаются (игнорируются), полученый скелет регуляризируется
с помощью операции стрижки с параметром PruningSize
*/
void BondSkeletTrans(
    BitRaster* InputImg /*указатель на исходный образ*/
    ,
    int PruningSize /*размер стрижки скелета*/
    ,
    int AreaIgnore /*площадь игнорируемых контуров*/
    ,
    TPolFigure*& Figure /*гранично-скелетное представление фигуры*/);
