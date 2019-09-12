// #include <unistd.h>
// #include <sys/wait.h>
#include "memtracker.h"
#include <map>
#include <algorithm>
#include <fstream>
#include <iterator>

// major things left to do:
// 1. handling globals
// 2. inspecting why lock_func_af doesn't work on locks - IPOINT_AFTER
// 3. making function invocation count threadwise - DONE
// 4. handling external references - DONE

std::map <std::string, int> locks;		// mutex -> type
std::map <int, std::string> unlocks;	// type -> mutex name

std::ofstream outp;						// file to write to

// should do routine wise for memory efficiency
std::map <ADDRINT, INSINFO> inslist;					// all instructions

std::map <THREADID, std::map<ADDRINT, int>> syncs;		// thread -> lock address -> mutex type

long long int timeStamp = 0;			// global event timestep

std::map <std::string, std::map<THREADID, int>> invMap;	// function invocation number


struct fnlog
{
	THREADID tid;
	std::string fname;
	int invNo;
	ADDRINT rbp;

	fnlog() {;}
	fnlog (std::string fn, THREADID t, ADDRINT bp) {fname = fn, tid = t, invNo = invMap[fn][t]; rbp = bp;}
	fnlog (std::string fn, THREADID t, int ino, ADDRINT bp) {fname = fn, tid = t, invNo = ino; rbp = bp;}
	void print(std::ostream& outf = std::cout) const {outf << "|" << tid << ":" << fname << ":" << invNo << ":" << rbp << "| ";}
	bool operator < (const fnlog& rhs) const
	{
		if (tid != rhs.tid) return tid < rhs.tid;
		if (fname != rhs.fname) return fname < rhs.fname;
		return invNo < rhs.invNo;
	}
};
std::map <ADDRINT, fnlog> RBPstack;
// std::map <fnlog, ADDRINT> fnstack;
std::map <THREADID, std::vector <fnlog>> invstack;

void printRBP (std::ostream& outf = std::cout)
{
	outf << "\n\nRBPSTACK\n\n";
	for (auto i: RBPstack)
	{
		outf << i.first << "->";
		i.second.print(outf);
	}
	outf << "\n\n";
}

// void printfn (std::ostream& outf = std::cout)
// {
// 	outf << "\n\nFNSTACK\n\n";
// 	for (auto i: fnstack)
// 	{
// 		i.first.print(outp);
// 		outf << "->" << i.second << " ";
// 	}
// 	outf << "\n\n";
// }

void printinv (std::ostream& outf = std::cout)
{
	outf << "\n\nINVSTACK\n\n";
	for (auto i: invstack)
	{
		outf << i.first << ": ";
		for (auto j: i.second)
			j.print(outf);
			outf << " -> ";
		outf << "\n";
	}
	outf << "\n\n";
}

void printall()
{
	printRBP(outp);
	// printfn(outp);
	printinv(outp);
}

// std::map <THREADID, std::vector <ADDRINT>> RBPstack;
// std::map <THREADID, std::vector <std::string>> fnstack;

struct variable
{
	std::string name;
	long long int id;
	ssize_t size;
	std::string fname;
	std::string type;
	long long int pid;
	std::string spattr;

	void print(std::ostream& outf = std::cout) 
	{outf << fname << ": " << type << " - " << name << ": " << id << " " << pid << "\n";};
};
std::map <std::string, std::map <ADDRINT, variable>> funcLocalMap;
std::map <ADDRINT, variable> globalMap;

std::map <ADDRINT, variable>::iterator lookup (std::map <ADDRINT, variable>& mymap, ADDRINT addr)
{
	std::map <ADDRINT, variable>::iterator it = mymap.upper_bound(addr);
	if (it != mymap.begin())
	{
		// outp << "\n\nADD: " << hex << it->first;
		it--;
		// outp << " " << hex << it->first << " ADD\n\n" << dec;

		// it = std::prev(it);
		ADDRINT diff = addr - it->first;
		ssize_t size = it->second.size;
		// if (diff != 0)
		// 	outp << "\n\nADD: " << hex << it->first << " " << addr << dec << " << DIFF: " << diff << " Size: " << size << "\n\n";
		if (size > diff)
			return it;
	}
	return mymap.end();
}


std::string goff = "_static.offset";
std::string off = "final.offset";

/*			variables in stack - need to do later to handle references
std::map <ADDRINT, std::string> stackMap; // address -> variable node id
std::map <ADDRINT, std::pair<std::string, int offset>> stackMap;	// address -> routine x offset
// ^ maybe a better implementation as it decouples offset map from pintool
std::vector <std::pair <ADDRINT, std::pair <std::string, int>>> stackMap;
// ^ also a possible implementation: sorted list of RBP x RoutineName x InvocationNo
// ^ possibly the best way to do it
*/

// void print_state (const std::ios& stream, std::ostream& outf = std::cout) {
//   outf << " good()=" << stream.good();
//   outf << " eof()=" << stream.eof();
//   outf << " fail()=" << stream.fail();
//   outf << " bad()=" << stream.bad();
//   outf << "\n";
// }


// basic initialization
VOID init(std::string locf)
{
	// set up the type maps
	locks["mutex"] = 1;
	locks["semaphore"] = 2;
	locks["reader lock"] = 3;
	locks["writer lock"] = 4;
	unlocks[1] = "MUTEX";
	unlocks[2] = "SEMAPHONE";
	unlocks[3] = "READLOCK";
	unlocks[4] = "WRITELOCK";

	// open the output file
	std::string opfile = locf + ".dump";
	outp.open(opfile.c_str());

	std::ifstream offFile(off.c_str());
	std::string fn;
	ADDRINT offset;
	variable var;

	while (!offFile.eof())
	{
		offFile >> fn >> offset >> var.id >> var.name;
		var.fname = fn;
		offFile.get();
		std::getline (offFile, var.type, '\t');
		offFile >> var.size >> var.pid;
		funcLocalMap[fn][offset] = var;
	}
	// for (auto i: funcLocalMap)
	// {
	// 	outp << i.first << "\n";
	// 	for (auto j : i.second)
	// 	{
	// 		outp << j.first << " ";
	// 		j.second.print(outp);
	// 	}
	// }
	// outp << "\n";

	offFile.close();

	offFile.open((locf+goff).c_str());
	while (offFile.good())
	{
		offFile >> hex >> offset >> dec >> var.name >> var.id;
		offFile.get();
		std::getline (offFile, var.type, '\t');
		offFile >> var.size >> var.pid >> var.spattr;
		if (var.spattr.find("STATIC") > 0)
			offFile >> var.fname;
		else
			var.fname = "";
		globalMap[offset] = var;
	}
	// for (auto j: globalMap)
	// {
	// 	outp << j.first << " ";
	// 	j.second.print(outp);
	// }
	// outp << "\n";
	
	offFile.close();
}

// update rbp on change
VOID updateRBP (ADDRINT ina, THREADID tid, ADDRINT rbpval) 
{
	fnlog f(RTN_FindNameByAddress(ina), tid, rbpval);
	RBPstack[rbpval] = f; 
	// fnstack[f] = rbpval;
	invstack[tid].push_back(f);

	// outp << "INVOKED UPDATERBP\n\n";
	// printall();

	// outp << "FOR TID: " << tid << " RBP updated to " << rbpval << "\n";
	// outp << "Routine Stack:\n";
	// for (auto name: fnstack[tid])
	// 	outp << name << " ";
	// outp << "\nRBP Stack\n";
	// for (auto rbp: RBPstack[tid])
	// 	outp << hex << rbp << " ";
	// outp << "\n";
}


// memory access event handler
VOID dataman (THREADID tid, ADDRINT ina, ADDRINT memOp)
{
	inslist[ina].memOp = memOp;		// set target memory address - helps in debugging later

	variable var;
	fnlog f;
	ADDRINT offset;
	bool found = false;
	bool stat = false;
	std::string accessType;
	std::map <ADDRINT, variable>::iterator it;

	// look in globals
	it = lookup(globalMap, memOp);
	if (it != globalMap.end())
	{
		var = it->second;
		accessType = var.spattr;
		found = true;
		stat = true;
	}
	else
	{
		// look in cuurent stack
		f = invstack[tid].back();
		offset = f.rbp - memOp;
		auto& curmap = funcLocalMap[f.fname];
		it = lookup(curmap, offset);
		if (it != curmap.end())
		{
			accessType = "LOCAL";	// local access
			var = it->second;
			found = true;
		}

		// look across other function invocations
		else
		{
			auto itstack = RBPstack.upper_bound(memOp);

			if (itstack != RBPstack.end())
			{
				f = itstack->second;
				offset = itstack->first - memOp;	// get offset from current RBP
				// lookup in funcLocals
				auto& offMap = funcLocalMap[f.fname];
				it = lookup(offMap, offset);
				if (it != offMap.end())
				{
					accessType = "NONLOCAL";	// nonlocal access
					var = it->second;
					found = true;
				}
				// else
				// 	outp << "VARSEARCH FAILED IN " << f.fname << "\n";
			}
		}
	}

	if (not found)
	{
		// outp << "VARIABLE NOT FOUND.... REAL ADDRESS: 0x" << hex << memOp << dec << ".\n";
		// inslist[ina].shortPrint(outp);
		return;
	}
	else
	{
		// inslist[ina].shortPrint(outp);
		
		// print event type
		if (inslist[ina].flag == 'r')
			outp << "READ";
		else if (inslist[ina].flag == 'w')
			outp << "WRITE";
		outp << " THREADID " << tid << " VARCLASS " << accessType;		// print thread id and access type
		if (stat)
		{
			if (accessType.find("STATIC") > 0)
				outp << " VARCONTAINER " << var.fname;
			outp << " ADDRESS 0x" << hex << memOp << dec;
		}
		else 
		{
			if (accessType == "NONLOCALSTACK")
				outp << " VARFUNCNAME " << f.fname << " VARFUNCTID " << f.tid << " VARFUNCINVNO " << f.invNo;
				// function linkage name PIN_UndecorateSymbolName(fnstack[tid][idx], UNDECORATION_NAME_ONLY)
			outp << " OFFSET 0x" << hex << offset << dec;
		}
		outp << " VARNAME " << var.name << " VARID " << var.id;
		outp << " FUNCNAME " << inslist[ina].rtnName;
		// synchronization info
		outp << " SYNCS ";
		if (syncs.find(tid) != syncs.end())
		{
			outp << syncs[tid].size() << " ";
			for (auto l: syncs[tid])
				outp << "ADDRESS 0x" << hex << l.first << dec << " TYPE " << unlocks[l.second] << " ";
		}
		else
			outp << "ASYNC ";

		outp << "id " << dec << ++timeStamp << " ";						// event timestamp
		outp << "INVNO " << invMap[inslist[ina].rtnName][tid] << "\n";	// function invocation count	
	}
}

// funcation call event handler
VOID callP (THREADID tid, ADDRINT ina)
{
	// invMap[inslist[ina].target][tid]++;							// one more invocation of target
	outp << "CALL THREADID " << tid << " ";							// event type and thread id
	outp << "CALLERNAME " << inslist[ina].rtnName << " ";			// caller linkage name
	outp << "CALLEENAME " << inslist[ina].target << " ";			// callee linkage name
	outp << "id " << dec << ++timeStamp << " ";						// event timestamp
	outp << "INVNO " << invMap[inslist[ina].rtnName][tid] << "\n";	// function invocation count
}

VOID invP (THREADID tid, ADDRINT ina)
{
	std::string rtnName = RTN_FindNameByAddress(ina);
	invMap[rtnName][tid]++;
	
	// exit(0);
	// fnstack[tid].push_back(rtnName);
	// RBPstack[tid].push_back(0);

	// outp << "Someone invoked. Routine Stack:\n";
	// for (auto name: fnstack[tid])
	// 	outp << name << " ";
	// outp << "\n";
}


VOID retP (THREADID tid, ADDRINT ina)
{
	// outp << "INVOKED RETP\n\n";
	// outp << "PREREMOVAL\n\n";
	// printall();

	ADDRINT bp = invstack[tid].back().rbp;
	invstack[tid].pop_back();
	if (invstack[tid].empty())
		invstack.erase(tid);
	// fnlog f(RTN_FindNameByAddress(ina), tid, ino);
	// ADDRINT rbpval = fnstack[f];
	// fnstack.erase(f);
	RBPstack.erase(bp);

	// outp << "POSTREMOVAL\n\n";
	// printall();

	// outp << "Someone returned. Routine Stack:\n";
	// for (auto name: fnstack[tid])
	// 	outp << name << " ";
	// for (auto rbp: RBPstack[tid])
	// 	outp << hex << rbp << " ";
	// outp << "\n";
}

// filters and saves instructions to instrument
VOID Instruction(INS ins, VOID * v)
{
	ADDRINT ina = INS_Address(ins);
	int column, line;
	std::string fname;

	PIN_LockClient();
	PIN_GetSourceLocation(ina, &column, &line, &fname);			// get source information
	PIN_UnlockClient();

	if (fname.length() > 0 && fname.find("/usr") == -1)		// instrument only instructions whose source location is available
	{
		if (inslist.find(ina) == inslist.end())
			inslist[ina] = INSINFO(ins, fname, column, line);	// add to list
		//inslist[ina].shortPrint(outp);

		// if it is a call event
		if (inslist[ina].target != "")
			INS_InsertCall(
			ins, IPOINT_BEFORE, (AFUNPTR)callP,
			IARG_THREAD_ID, IARG_ADDRINT, ina,
			IARG_END);

		// if it updates rbp
		int t = inslist[ina].rbploc;

		if (t != -1)
		{
			//inslist[ina].shortPrint(outp);
			INS_InsertCall(
			ins, IPOINT_AFTER, (AFUNPTR)updateRBP,
			IARG_ADDRINT, ina, IARG_THREAD_ID,
			IARG_REG_VALUE, INS_RegW(ins, t),
			IARG_END);
		}
			

		// if it is a memory access
		if (inslist[ina].flag != 'n')
			INS_InsertCall(
			ins, IPOINT_BEFORE, (AFUNPTR)dataman,
			IARG_THREAD_ID, IARG_ADDRINT, ina,
			IARG_MEMORYOP_EA, 0,
			IARG_END);

		if (INS_IsRet(ins))
			INS_InsertCall(
			ins, IPOINT_BEFORE, (AFUNPTR)retP, 
			IARG_THREAD_ID, IARG_INST_PTR, 
			IARG_END);
		
		// else
		// 	INS_InsertCall(
		// 	ins, IPOINT_BEFORE, (AFUNPTR)dataman,
		// 	IARG_THREAD_ID, IARG_ADDRINT, ina,
		// 	IARG_ADDRINT, -1,
		// 	IARG_END);
	}
}

// synchronization lock acquisition event handler
VOID lock_func_bf (THREADID tid, ADDRINT addr, int type, ADDRINT rta)
{
	syncs[tid][addr] = type;													// thread id and lock variable address
	outp << "LOCK TID " << tid << " ADDRESS 0x" << hex << addr;					// event record
	outp << " TYPE " << unlocks[type] << " id " << dec << ++timeStamp << "\n";
}

/*		need to check out why this does not work
VOID lock_func_af (THREADID tid, ADDRINT addr, int type, ADDRINT rta)
{
	PIN_LockClient();
	RTN rtn = RTN_FindByAddress(rta);
	RTN_Open(rtn);
	INS ins = RTN_InsHead(rtn);
	RTN_Close(rtn);
	PIN_UnlockClient();
	INSINFO l(ins);
	outp << "MILA MILA!!!!! DOOSRA!!\n";
	l.print();
	outp << "\n\n";

	syncs[tid][addr] = type;
	outp << "setting syncs " << tid << " " << addr << "\n";
}*/

// synchronization lock release event handler
VOID unlock_func(THREADID tid, ADDRINT addr, ADDRINT rta)
{
	// if (syncs.find(tid) == syncs.end())
	// 	outp << "\n\nDAFUQ!!\n";
	// else
	// {
		outp << "UNLOCK TID " << tid << " ADDRESS 0x" << hex << addr;			// event record
		outp << " TYPE " << unlocks[syncs[tid][addr]] << " id " << dec << ++timeStamp << "\n";
		auto loc = syncs[tid].find(addr);				// unset the locks for thread
		syncs[tid].erase(loc);
		if (syncs[tid].size() == 0)						// remove thread from list if it holds no locks
			syncs.erase(syncs.find(tid));
	// }
}

// Looking for POSIX locking mechanisms
VOID Routine (RTN rtn, VOID * v)
{
	ADDRINT rta = RTN_Address(rtn);

	int column, line;
	std::string fname;

	PIN_LockClient();
	PIN_GetSourceLocation(rta, &column, &line, &fname);			// get source information
	PIN_UnlockClient();

	if (fname.length() > 0 && fname.find("/usr") == -1)		// instrument only instructions whose source location is available
	{
		RTN_Open(rtn);
		// string rtnName = RTN_Name(rtn);
		// outp << fname << "\n" << rtnName << "\n";
		
		// for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins))
		// {
		// 	ADDRINT ina = INS_Address(ins);
		// 	PIN_LockClient();
		// 	PIN_GetSourceLocation(ina, &column, &line, &fname);			// get source information
		// 	PIN_UnlockClient();
		// 	INSINFO(ins, fname, column, line).print(outp);
		// }

		RTN_InsertCall(rtn, IPOINT_BEFORE,
			(AFUNPTR)invP, IARG_THREAD_ID,
			IARG_ADDRINT, rta, IARG_END);

		// for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins))
		// 	if (INS_IsRet(ins))
		// 		INS_InsertCall(ins, IPOINT_BEFORE,
		// 		(AFUNPTR)retP, IARG_THREAD_ID,
		// 		IARG_INST_PTR, IARG_END);

		RTN_Close(rtn);
	}

	// if any of these locking functions is called
	std::string rname = RTN_Name(rtn), pat = "";
	if (rname == "pthread_mutex_lock@plt")
		pat = "mutex";
	else if (rname == "sem_wait")
		pat = "semaphore";
	else if (rname == "__pthread_rwlock_rdlock")
		pat = "reader lock";
	else if (rname == "__pthread_rwlock_wrlock")
		pat = "writer lock";

	// call the lock acquisition event handler
	if (pat != "")
	{
		RTN_Open(rtn);
		RTN_InsertCall(rtn, IPOINT_BEFORE,
			(AFUNPTR)lock_func_bf,
			IARG_THREAD_ID, IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
			IARG_UINT64, locks[pat], IARG_INST_PTR,
			IARG_END);
		// RTN_InsertCall(rtn, IPOINT_AFTER,
		// 	(AFUNPTR)lock_func_af,
		// 	IARG_THREAD_ID, IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
		// 	IARG_UINT64, locks[pat], IARG_INST_PTR,
		// 	IARG_END);
		RTN_Close(rtn);
	}

	// if any of the unlocking functions is called
	if (rname == "pthread_mutex_unlock@plt" || rname == "thread_rwlock_unlock" || rname == "sem_post")
	{
		// call the lock release event handler
	 	RTN_Open(rtn);
		RTN_InsertCall (rtn, IPOINT_BEFORE,
			(AFUNPTR) unlock_func,
			IARG_THREAD_ID, IARG_FUNCARG_ENTRYPOINT_VALUE, 0,
			IARG_INST_PTR, IARG_END);
		RTN_Close(rtn);
	}
}

/*		now decoupled from pintool
void initMaps (std::string locf)
{
	std::string opfile = locf + ".dump";
	outp.open(opfile.c_str());

	int ofst;
	std::string varfile = locf + "_combined.offset", func, id;
	std::ifstream vars(varfile.c_str());

	if (vars.is_open())
	{
		while (!vars.eof())
		{
			vars >> func >> ofst >> id;
			varmap[func][ofst] = id;
		}
		vars.close();
	}
	else
	{
		std::outp << "No such file " << varfile << "\n";
		// exit(1);
	}
}
*/

// close output file on exit
VOID Fini (INT32 code, VOID * v)
{
	outp.close();
}

int main(int argc, char * argv[])
{
	// Initialize pin & symbol manager
	PIN_Init(argc, argv);
	PIN_InitSymbols();

	// get the executable name
	std::string u(argv[argc-1]);
	std::string locf = u.substr(u.find_last_of("/") + 1, u.find_last_of(".") - u.find_last_of("/") - 1);
	// basic variable initializations
	init(locf);
	// initMaps(locf);

	RTN_AddInstrumentFunction(Routine, 0);		// Routine level Instrumentation for locking and invocation events
	INS_AddInstrumentFunction(Instruction, 0);	// Instruction level Instrumentation for all other events
	PIN_AddFiniFunction(Fini, 0);				// Closing output file at the end
	
	// Start the program, never returns
	PIN_StartProgram();

	return 0;
}
