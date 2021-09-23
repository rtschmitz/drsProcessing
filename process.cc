#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <math.h>
#include <cmath>
#include <iostream>
#include <fstream>
typedef struct {
   char           tag[3];
   char           version;
} FHEADER;

typedef struct {
   char           time_header[4];
} THEADER;

typedef struct {
   char           bn[2];
   unsigned short board_serial_number;
} BHEADER;

typedef struct {
   char           event_header[4];
   unsigned int   event_serial_number;
   unsigned short year;
   unsigned short month;
   unsigned short day;
   unsigned short hour;
   unsigned short minute;
   unsigned short second;
   unsigned short millisecond;
   unsigned short range;
} EHEADER;

typedef struct {
   char           tc[2];
   unsigned short trigger_cell;
} TCHEADER;

typedef struct {
   char           c[1];
   char           cn[3];
} CHEADER;

int read_binary(char[256],bool);
/*-----------------------------------------------------------------------------*/

int main(int argc, const char * argv[])
{
   bool waveOut=false;
   char filename[256];
   if (argc > 1){
      strcpy(filename, argv[1]);
   if (argc>2) waveOut=argv[2];
   }
   else {
      printf("Usage: process <filename> <waveformOutBool>\n");
      return 0;
   }

  return read_binary(filename,waveOut);

}
int read_binary(char filename[256],bool waveOut)
{
   FHEADER  fh;
   THEADER  th;
   BHEADER  bh;
   EHEADER  eh;
   TCHEADER tch;
   CHEADER  ch;
   
   unsigned int scaler;
   unsigned short voltage[1024];
   double waveform[16][4][1024], time[16][4][1024];
   float bin_width[16][4][1024];
   int n_chans, i, j, b, chn, n, chn_index, n_boards;
   double t1, t2, dt, vmax;
   int binmax;
   vmax=0;
   int ndt;
   double threshold, sumdt, sumdt2;
   std::ofstream outfile;
   if(waveOut) outfile.open("processed.txt");
   
   // open the binary waveform file
   FILE *f = fopen(filename, "rb");
   if (f == NULL) {
      printf("Cannot find file \'%s\'\n", filename);
      return 0;
   }

   // read file header
   fread(&fh, sizeof(fh), 1, f);
   if (fh.tag[0] != 'D' || fh.tag[1] != 'R' || fh.tag[2] != 'S') {
      printf("Found invalid file header in file \'%s\', aborting.\n", filename);
      return 0;
   }
   
   if (fh.version != '2') {
      printf("Found invalid file version \'%c\' in file \'%s\', should be \'2\', aborting.\n", fh.version, filename);
      return 0;
   }

   // read time header
   fread(&th, sizeof(th), 1, f);
   if (memcmp(th.time_header, "TIME", 4) != 0) {
      printf("Invalid time header in file \'%s\', aborting.\n", filename);
      return 0;
   }

   for (b = 0 ; ; b++) {
      // read board header
      fread(&bh, sizeof(bh), 1, f);
      if (memcmp(bh.bn, "B#", 2) != 0) {
         // probably event header found
         fseek(f, -4, SEEK_CUR);
         break;
      }
      
      printf("Found data for board #%d\n", bh.board_serial_number);
      
      // read time bin widths
      memset(bin_width[b], sizeof(bin_width[0]), 0);
      for (chn=0 ; chn<5 ; chn++) {
         fread(&ch, sizeof(ch), 1, f);
         if (ch.c[0] != 'C') {
            // event header found
            fseek(f, -4, SEEK_CUR);
            break;
         }
         i = ch.cn[2] - '0' - 1;
         printf("Found timing calibration for channel #%d\n", i+1);
         fread(&bin_width[b][i][0], sizeof(float), 1024, f);
         // fix for 2048 bin mode: double channel
         if (bin_width[b][i][1023] > 10 || bin_width[b][i][1023] < 0.01) {
            for (j=0 ; j<512 ; j++)
               bin_width[b][i][j+512] = bin_width[b][i][j];
         }
      }
   }
   n_boards = b;
   n_chans = i+1;
   // labels
   if(waveOut){
	outfile << "NCHANS: " << n_chans << std::endl;
	outfile << "labels: EVTNUM BOARD_CHAN TIMESTAMP vMAX(mV) tMAX(ns) SCALER" << std::endl;
   }   

   // loop over all events in the data file
   for (n=0 ; ; n++) {
//	std::cout << "file position: " << ftell(f) << std::endl;
      // read event header
      i = (int)fread(&eh, sizeof(eh), 1, f);
      if (i < 1)
         break;
      
//      printf("Found event #%d %d %d\n", eh.event_serial_number, eh.second, eh.millisecond);
      
      // loop over all boards in data file
      for (b=0 ; b<n_boards ; b++) {
         
         // read board header
         fread(&bh, sizeof(bh), 1, f);
         if (memcmp(bh.bn, "B#", 2) != 0) {
            printf("Invalid board header in file \'%s\', aborting.\n", filename);
            return 0;
         }
         
         // read trigger cell
         fread(&tch, sizeof(tch), 1, f);
         if (memcmp(tch.tc, "T#", 2) != 0) {
            printf("Invalid trigger cell header in file \'%s\', aborting.\n", filename);
            return 0;
         }

         if (n_boards > 1)
            printf("Found data for board #%d\n", bh.board_serial_number);
         
         // reach channel data
         for (chn=0 ; chn<4 ; chn++) {
            
            // read channel header
            fread(&ch, sizeof(ch), 1, f);
            if (ch.c[0] != 'C') {
               // event header found
               fseek(f, -4, SEEK_CUR);
               break;
            }
            chn_index = ch.cn[2] - '0' - 1;
            fread(&scaler, sizeof(int), 1, f);
            fread(voltage, sizeof(short), 1024, f);
            
            for (i=0 ; i<1024 ; i++) {
               // convert data to volts
               waveform[b][chn_index][i] = 1000*(voltage[i] / 65536. + eh.range/1000.0 - 0.5);
               if(std::abs(waveform[b][chn_index][i])>vmax) {vmax=std::abs(waveform[b][chn_index][i]); binmax=i;}

               // calculate time for this cell
               for (j=0,time[b][chn_index][i]=0 ; j<i ; j++)
                  time[b][chn_index][i] += bin_width[b][chn_index][(j+tch.trigger_cell) % 1024];
            }

	//////////////////////////////////////////////////////////////////////////////////////////////////
	//					channel analysis					//
	//////////////////////////////////////////////////////////////////////////////////////////////////




	//////////////////////////////////////////////////////////////////////////////////////////////////
	//					print waveform						//
	//////////////////////////////////////////////////////////////////////////////////////////////////
	if(waveOut){	
	    outfile << "waveform: " << n << " " << bh.board_serial_number
		<< "_" << chn+1 << " " << eh.year << "." << eh.month << "." << eh.day << "." << eh.hour << "." << eh.minute << "." << eh.second
		<< "." << eh.second << "." << eh.millisecond << " " << vmax << " " << time[b][chn_index][binmax] << " " << scaler << std::endl;
         
		for(int tt=0;tt<1024;tt++){
			outfile << time[b][chn_index][tt] << "	" << waveform[b][chn_index][tt] << std::endl;
	 	}
            }
	vmax=0;  
         }
	}
   }
   
   return 1;
}

