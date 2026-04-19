# EXTERNAL DEPENDENCIES

## Supabase (PostgreSQL Database)
**Type**: Database  
**Status**: ⏳ Not Connected  
**Version**: PostgreSQL (via Supabase free tier)  
**Purpose**: Store committees and delegates data  
**Critical**: Yes  
**Activation**: Phase 1  

### Configuration Required
- Database URL (environment variable)
- Connection pooling settings
- Migration scripts

### Risks
- Free tier limitations
- Connection limits
- Data persistence

### Mitigation
- Monitor usage
- Plan for scaling if needed
- Regular backups

---

## Render.com (Hosting)
**Type**: Hosting Platform  
**Status**: ⏳ Not Connected  
**Version**: Free tier  
**Purpose**: Deploy FastAPI application  
**Critical**: Yes  
**Activation**: Phase 4  

### Configuration Required
- GitHub repository connection
- Environment variables
- Build commands
- Start commands

### Risks
- Free tier limitations (sleep after inactivity)
- Cold start delays
- Resource constraints

### Mitigation
- Accept free tier limitations for Phase 0
- Plan for paid tier if needed
- Optimize cold start time

---

## Python 3.11
**Type**: Runtime  
**Status**: ⏳ Not Verified  
**Version**: 3.11+  
**Purpose**: Backend runtime  
**Critical**: Yes  
**Activation**: Phase 1  

### Configuration Required
- Virtual environment setup
- Package installation (requirements.txt)

### Risks
- Version compatibility issues
- Package conflicts

### Mitigation
- Use virtual environment
- Pin package versions
- Test locally before deployment

---

## FastAPI
**Type**: Web Framework  
**Status**: ⏳ Not Installed  
**Version**: Latest stable  
**Purpose**: Backend API framework  
**Critical**: Yes  
**Activation**: Phase 1  

### Configuration Required
- Install via pip
- Configure CORS
- Configure middleware

### Risks
- Breaking changes in updates
- Performance issues

### Mitigation
- Pin version in requirements.txt
- Test thoroughly
- Monitor performance

---

## SQLAlchemy
**Type**: ORM  
**Status**: ⏳ Not Installed  
**Version**: Latest stable  
**Purpose**: Database ORM  
**Critical**: Yes  
**Activation**: Phase 1  

### Configuration Required
- Install via pip
- Configure engine
- Define models

### Risks
- Query performance
- Migration complexity

### Mitigation
- Use SELECT FOR UPDATE for race conditions
- Test migrations thoroughly
- Monitor query performance

---

## Pydantic
**Type**: Validation Library  
**Status**: ⏳ Not Installed  
**Version**: Latest stable  
**Purpose**: Input validation  
**Critical**: Yes  
**Activation**: Phase 1  

### Configuration Required
- Install via pip
- Define schemas

### Risks
- Validation performance
- Complex validation rules

### Mitigation
- Keep validation simple
- Test edge cases
- Monitor performance
