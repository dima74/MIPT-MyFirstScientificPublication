#include <QString>
#include <QVector>

#include "SkeletonLib/BSTrans.h"

class PatternSpectrum {
 public:
  PatternSpectrum(
      int area, double step, int _class_label,
      const string &_output_filename, double _pruning);
  ~PatternSpectrum();
  void ProcessImage(QString path);

 private:
  QString imagepath;
  FILE* fid;
  QImage image;
  TPolFigure* skeleton;
  BitRaster* srcimg;

  int area;
  double step;
  double rMax;
  int class_label;
  string output_filename;
  double pruning;

  QVector<double> radiuses;
  QVector<double> values;

  void CalcSpectrum();
  void ReportSkeleton();
  void ReportContour();
};
