#include "PatternSpectrum.h"
#include <vector>
#include <fstream>
#include <algorithm>
#include <string>

using std::vector;
using std::fstream;
using std::ofstream;
using std::copy;
using std::vector;
using std::ostream_iterator;
using std::string;

PatternSpectrum::PatternSpectrum(
    int a, double s, int _class_label, 
    const string &_output_filename, double _pruning)
    : skeleton(nullptr), srcimg(nullptr), area(a),
      step(s), rMax(-1), class_label(_class_label),
      output_filename(_output_filename), pruning(_pruning) {}

PatternSpectrum::~PatternSpectrum() {}

void PatternSpectrum::ProcessImage(QString path) {
  imagepath = path;
  image = QImage(imagepath);
  if (skeleton != nullptr) {
    delete skeleton;
  }
  if (srcimg) {
    delete srcimg;
  }
  srcimg = new BitRaster(image.width(), image.height());
  for (int i = 0; i < image.height(); i++) {
    for (int j = 0; j < image.width(); j++) {
      bool isBlack = qGray(image.pixel(j, i)) < 128;
      if (isBlack) {
        srcimg->setBit(j, i, isBlack);
      }
    }
  }

  // clock_t time0 = clock();
  BondSkeletTrans(srcimg, pruning, area, skeleton);
  //skeleton->MakeNodeBoneRepresentation();
  // clock_t time1 = clock();
      ReportSkeleton();
      ofstream fout(output_filename, ofstream::app);
      fout << endl;
          /*skeleton->MonotonicSubdivision();
          CalcSpectrum();
          ofstream fout(output_filename, ofstream::app);
          for (int i = 0; i < radiuses.size(); ++i) {
            fout << radiuses[i] << ' ' << values[i] << ' ';
          }
          fout << endl;
          fout.close();*/
  // clock_t time2 = clock();
  //skeleton->CutSkeleton(0.1);
  /*vector<double> angles = skeleton->GetContourAngles();
  vector<double> lengths = skeleton->GetContourLengths();
  //int index = imagepath.lastIndexOf('.');
  //ofstream fout((imagepath.left(index) + ".txt").toLocal8Bit().constData(), ofstream::app);
  ofstream fout(output_filename, ofstream::app);
  fout << class_label << ' ';

  copy(angles.begin(), angles.end(), ostream_iterator<double>(fout, " "));
  copy(lengths.begin(), lengths.end(), ostream_iterator<double>(fout, " "));
  fout << endl;
  fout.close();*/
  /*int index = imagepath.lastIndexOf('.');
  QByteArray ba = (imagepath.left(index) + ".bin").toLocal8Bit();
  char* reportpath = ba.data();
  fid = fopen(reportpath, "wb");
  int len = values.size();
  fwrite(&len, sizeof(int), 1, fid);
  fwrite(radiuses.data(), sizeof(double), len, fid);
  fwrite(values.data(), sizeof(double), len, fid);
  fclose(fid);*/
}

bool CompareOrg(TBone* BoneA, TBone* BoneB) {
  return BoneA->org->r() < BoneB->org->r();
}

bool CompareDest(TBone* BoneA, TBone* BoneB) {
  return BoneA->dest->r() < BoneB->dest->r();
}

void PatternSpectrum::CalcSpectrum() {
  skeleton->AllBones.sort(CompareOrg);
  rMax = (*max_element(skeleton->AllBones.begin(), skeleton->AllBones.end(),
                       CompareDest))
             ->dest->r();
  int nSteps = floor((rMax + 1e-6) / step) + 1;
  radiuses.resize(nSteps + 1);
  values.resize(nSteps + 1);

  for (int iRad = 0; iRad < nSteps + 1; iRad++) {
    // if (iRad == nSteps)
    // double w = 1;

    double radius = iRad * step;
    radiuses[iRad] = radius;
    values[iRad] = 0;

    cerr << skeleton->AllBones.size() << endl;
    for (auto iBone = skeleton->AllBones.begin();
         iBone != skeleton->AllBones.end() && radius > (*iBone)->org->r();
         iBone++) {
      if ((*iBone)->lacuna == nullptr) {
        // Бицикл стал усеченным
        for (int i = 0; i < 3 && (*iBone)->org->Bones[i] != nullptr &&
                        (*iBone)->lacuna == nullptr;
             i++) {
          if ((*iBone)->org->Bones[i]->lacuna != nullptr) {
            (*iBone)->lacuna = (*iBone)->org->Bones[i]->lacuna;
          }
        }
        if ((*iBone)->lacuna == nullptr) {
          (*iBone)->lacuna = new Lacuna();
          skeleton->Lacunas.push_back((*iBone)->lacuna);
        }
        (*iBone)->lacuna->AddBone(*iBone, radius);
      }
      if ((*iBone)->dest->r() < radius) {
        // Бицикл полностью пропал
        Lacuna* BigLac = (*iBone)->lacuna;
        for (int i = 0; i < 3 && (*iBone)->dest->Bones[i] != nullptr; i++) {
          if ((*iBone)->dest->Bones[i]->lacuna != nullptr) {
            if ((*iBone)->dest->Bones[i]->lacuna->Bones.size() >
                BigLac->Bones.size())
              BigLac = (*iBone)->dest->Bones[i]->lacuna;
          }
        }
        for (int i = 0; i < 3 && (*iBone)->dest->Bones[i] != nullptr; i++) {
          if ((*iBone)->dest->Bones[i]->lacuna != nullptr)
            BigLac->Absorb((*iBone)->dest->Bones[i]->lacuna, radius);
        }
      }
    }

    auto iBone = skeleton->AllBones.begin();
    while (iBone != skeleton->AllBones.end()) {
      values[iRad] += (*iBone)->Square(radius);
      if ((*iBone)->dest->r() < radius)
        iBone = skeleton->AllBones.erase(iBone);
      else
        iBone++;
    }

    auto iLacn = skeleton->Lacunas.begin();
    while (iLacn != skeleton->Lacunas.end()) {
      if ((*iLacn)->Bones.empty())
        iLacn = skeleton->Lacunas.erase(iLacn);
      else {
        auto iBone = (*iLacn)->Truncated.begin();
        while (iBone != (*iLacn)->Truncated.end()) {
          if ((*iBone)->dest->r() < radius)
            iBone = (*iLacn)->Truncated.erase(iBone);
          else {
            values[iRad] += (*iBone)->SectorArea(radius);
            iBone++;
          }
        }

        // Ищем пересечения всех пар линз
        auto Pair = (*iLacn)->Pairs.begin();
        while (Pair != (*iLacn)->Pairs.end()) {
          double sub = PairSquare((*Pair).first, (*Pair).second, radius);
          if (sub > 0) {
            values[iRad] -= sub;
            Pair++;
          } else
            Pair = (*iLacn)->Pairs.erase(Pair);
        }

        iLacn++;
      }
    }
  }
}

void PatternSpectrum::ReportSkeleton() {
  ofstream fout(output_filename, ofstream::app);
  int index = imagepath.lastIndexOf('.');
  QByteArray ba = (imagepath.left(index) + "_skel.dat").toLocal8Bit();
  char* reportpath = ba.data();

  FILE* fid = fopen(reportpath, "wb");
  int n = skeleton->Components->cardinal();
  fwrite(&n, sizeof(int), 1, fid);
  TConnected* Com = skeleton->Components->first();
  double params[14];
  while (Com != nullptr) {
    int k = Com->Bones->cardinal();
    fwrite(&k, sizeof(int), 1, fid);
    TBone* Bone = Com->Bones->first();
    while (Bone != nullptr) {
      Bone->DetermineType();
      fwrite(&(Bone->type), sizeof(int), 1, fid);
      params[0] = Bone->org->X(); // x
      params[1] = Bone->org->Y(); // y
      params[2] = Bone->org->r(); // r
      params[3] = Bone->dest->X();
      params[4] = Bone->dest->Y();
      params[5] = Bone->dest->r();
      NodeKind kind1 =  Bone->org->Kind(), kind2 = Bone->dest->Kind();
      fout << params[0] << ' ' << params[1] << ' ' << kind1 << ' ' << params[2] << ' '
          << params[3] << ' ' << params[4] << ' ' << kind2 << ' ' << params[5] << ' ';
      int idxV,
          idxE;  // По каким индексам расположены сайт-точка и сайт-сегмент

      switch (Bone->type) {
        case BoneType::Linear:
          params[6] = ((TEdge*)Bone->Sites[0])->org->X;
          params[7] = ((TEdge*)Bone->Sites[0])->org->Y;
          params[8] = ((TEdge*)Bone->Sites[0])->dest->X;
          params[9] = ((TEdge*)Bone->Sites[0])->dest->Y;
          params[10] = ((TEdge*)Bone->Sites[1])->org->X;
          params[11] = ((TEdge*)Bone->Sites[1])->org->Y;
          params[12] = ((TEdge*)Bone->Sites[1])->dest->X;
          params[13] = ((TEdge*)Bone->Sites[1])->dest->Y;
          fwrite(params, sizeof(double), 14, fid);
          break;
        case BoneType::Parabolic:
          if (Bone->Sites[0]->IsVertex()) {
            idxV = 0;
            idxE = 1;
          } else {
            idxV = 1;
            idxE = 0;
          }
          params[6] = ((TVertex*)Bone->Sites[idxV])->p->X;
          params[7] = ((TVertex*)Bone->Sites[idxV])->p->Y;
          params[8] = ((TEdge*)Bone->Sites[idxE])->org->X;
          params[9] = ((TEdge*)Bone->Sites[idxE])->org->Y;
          params[10] = ((TEdge*)Bone->Sites[idxE])->dest->X;
          params[11] = ((TEdge*)Bone->Sites[idxE])->dest->Y;
          fwrite(params, sizeof(double), 12, fid);
          break;
        case BoneType::Hyperbolic:
          params[6] = ((TVertex*)Bone->Sites[0])->p->X;
          params[7] = ((TVertex*)Bone->Sites[0])->p->Y;
          params[8] = ((TVertex*)Bone->Sites[1])->p->X;
          params[9] = ((TVertex*)Bone->Sites[1])->p->Y;
          fwrite(params, sizeof(double), 10, fid);
          break;
      }
      Bone = Bone->getNext();
    }
    Com = Com->getNext();
  }
  fclose(fid);
  fout.close();
}

void PatternSpectrum::ReportContour() {
  int index = imagepath.lastIndexOf('.');
  QByteArray ba = (imagepath.left(index) + "_cont.dat").toLocal8Bit();
  char* reportpath = ba.data();

  FILE* fid = fopen(reportpath, "wb");
  int n = skeleton->Components->cardinal();
  fwrite(&n, sizeof(int), 1, fid);
  double coords[2];
  TConnected* Com = skeleton->Components->first();
  while (Com != nullptr) {
    int m = Com->HoleList.size() + 1;
    fwrite(&m, sizeof(int), 1, fid);
    int k = Com->Border->ListPoints->cardinal();
    fwrite(&k, sizeof(int), 1, fid);
    Point* Point = Com->Border->ListPoints->first();
    while (Point != nullptr) {
      coords[0] = Point->X;
      coords[1] = Point->Y;
      fwrite(coords, sizeof(double), 2, fid);
      Point = Point->getNext();
    }
    for (int i = 0; i < static_cast<int>(Com->HoleList.size()); i++) {
      int k = Com->HoleList[i]->ListPoints->cardinal();
      fwrite(&k, sizeof(int), 1, fid);
      Point = Com->HoleList[i]->ListPoints->first();
      while (Point != nullptr) {
        coords[0] = Point->X;
        coords[1] = Point->Y;
        fwrite(coords, sizeof(double), 2, fid);
        Point = Point->getNext();
      }
    }
    Com = Com->getNext();
  }
  fclose(fid);
}
