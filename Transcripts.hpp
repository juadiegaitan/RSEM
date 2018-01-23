/* Copyright (c) 2017
   Bo Li (The Broad Institute of MIT and Harvard)
   libo@broadinstitute.org

   This program is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License as
   published by the Free Software Foundation; either version 3 of the
   License, or (at your option) any later version.

   This program is distributed in the hope that it will be useful, but
   WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
   General Public License for more details.   

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
   USA
*/

/*
 * transcripts are numbered from 1. 0 is reserved for noise isoform
 */
#ifndef TRANSCRIPTS_H_
#define TRANSCRIPTS_H_

#include <cassert>
#include <string>
#include <vector>
#include <algorithm>

#include "Transcript.hpp"

class Transcripts {
public:
	Transcripts(int type = 0) {
		M = 0; this->type = type;
		transcripts.clear();
		transcripts.push_back(Transcript());
	}

	int getM() const { return M; }

	// used in shrinking the transcripts
	void setM(int M) { this->M = M; transcripts.resize(M + 1); } 
	
	void move(int from, int to) {
		assert(from >= to);
		if (from > to) transcripts[to] = transcripts[from];
	}
	
	int getType() const { return type; }
	void setType(int type) { this->type = type; }

	bool isAlleleSpecific() const { return type == 2; }

	const Transcript& getTranscriptAt(int pos) const {
		assert(pos > 0 && pos <= M);
		return transcripts[pos];
	}

	void add(const Transcript& transcript) {
		transcripts.push_back(transcript);
		++M;
	}

	void sort() {
		std::sort(transcripts.begin(), transcripts.end());
	}

	void readFrom(const char*);
	void writeTo(const char*);

	void updateCLens(); // update clen for each transcript record
	
private:
	int M, type; // type 0 from genome, 1 standalone transcriptome, 2 allele-specific 
	std::vector<Transcript> transcripts;
};

#endif /* TRANSCRIPTS_H_ */
