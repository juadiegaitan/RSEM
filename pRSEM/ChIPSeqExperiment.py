__doc__="""

  pliu 20150511

  python module for a ChIP-seq experiment that contains
  replicates of ChIP-seq data for target and/or control
"""

import ChIPSeqReplicate
import File
import Util

class ChIPSeqExperiment:
  def __init__(self):
    self.param = None ## reference to input parameters
    self.target_reps  = []
    self.control_reps = []
    self.fta_target_pool  = None  ## pooled tagAlign File object for target
    self.fta_control_pool = None  ## pooled tagAlign File object for control


  @classmethod
  def initFromParam(cls, param):
    cse = cls()
    cse.param = param
    ftgts = param.chipseq_target_read_files.split(',')
    cse.target_reps = [ ChIPSeqReplicate.initFromFastqFile(ffq) \
                        for ffq in ftgts ]
    for (i, rep) in enumerate(cse.target_reps):
      rep.param = param
      rep.index = i+1
      rep.is_control = False
      rep.chipseqexp = cse
      tgt_fta = "%s/%s.tagAlign.gz" % (param.temp_dir, rep.name)
      rep.tagalign = File.initFromFullFileName(tgt_fta)

    if param.chipseq_control_read_files is not None:
      fctrls = param.chipseq_control_read_files.split(',')
      cse.control_reps = [ ChIPSeqReplicate.initFromFastqFile(ffq) \
                           for ffq in fctrls ]
      for (i, rep) in enumerate(cse.control_reps):
        rep.param = param
        rep.index = i+1
        rep.is_control = True
        rep.chipseqexp = cse
        ctrl_fta = "%s/%s.tagAlign.gz" % (param.temp_dir, rep.name)
        rep.tagalign = File.initFromFullFileName(ctrl_fta)

    return cse


  def getFastqEncoding(self):
    nthr = self.param.num_threads
    fenc = self.param.imd_name + '_prsem.chipseq_encoding'
    fin = ','.join([ f.fastq.fullname for f in self.target_reps])
    if len(self.control_reps) > 0:
      fin = '%s,%s' % (fin, ','.join([ f.fastq.fullname \
                                       for f in self.control_reps]))

    Util.runCommand(self.param.chipseq_rscript, 'guessFqEncoding',
                    nthr, fin, fenc)

    with open(fenc, 'r') as f_fenc:
      next(f_fenc)
      file2enc = dict([ line.rstrip("\n").split("\t") for line in f_fenc ])

    for f in self.target_reps + self.control_reps:
      f.encoding = file2enc[f.fastq.fullname]


  def alignReadByBowtie(self):
    import os
    if self.param.num_threads > 4:
      nthr_bowtie = self.param.num_threads - 4
    else:
      nthr_bowtie = 1

    bowtie_ref_name = "%s_prsem" % self.param.ref_name
    for rep in self.target_reps + self.control_reps:
      if rep.fastq.is_gz:
        cmd_cat = 'zcat'
      else:
        cmd_cat = 'cat'

      ## many pipes, have to use os.system
      cmds = [ "%s %s |" % (cmd_cat, rep.fastq.fullname) ] + \
             [ "%s -q -v 2 -a --best --strata -m 1 %s -S -p %d %s - |" % (
               self.param.bowtie_bin_for_chipseq, rep.encoding, nthr_bowtie,
               bowtie_ref_name ) ] + \
             [ "%s view -S -b -F 1548 - |" % self.param.samtools_bin ] + \
             [ "%s bamtobed -i stdin |" % (
               self.param.bedtools_bin_for_chipseq ) ] + \
             [ """awk 'BEGIN{FS="\\t";OFS="\\t"}{$4="N"; print $0}' |""" ] + \
             [ "gzip -c > %s " % rep.tagalign.fullname ]

      cmd = ' '.join(cmds)
      print cmd;
      os.system(cmd)


def initFromParam(param):
  return ChIPSeqExperiment.initFromParam(param)


